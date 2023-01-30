import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
import math
import imutils
from IPython import display
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
from PIL import Image, ExifTags

# ---------------------------------
# GEOMETRY TOOLS
# ---------------------------------

def distanceCalculate(p):
    p1 = p[0]
    p2 = p[1]
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    return dis

def angleLinePoints(p):
    p1 = p[0]
    p2 = p[1]
    # 
    p1_x = p1[0]
    p1_y = p1[1]
    p2_x = p2[0]
    p2_y = p2[1]
    # 
    d_x = p2_x - p1_x
    d_y = p2_y - p1_y
    # 
    angle_radians = np.arctan(d_y/d_x)
    angle_degrees = math.degrees(angle_radians)
    return angle_degrees

def area_px_within_polyline(stacked_array):
    x = [stacked_array[0] for stacked_array in stacked_array]
    y = [stacked_array[1] for stacked_array in stacked_array]
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def focal_length_calculator(measured_distance, real_width, width_in_rf_image):
    # https://www.geeksforgeeks.org/realtime-distance-estimation-using-opencv-python/
    focal_length = (width_in_rf_image* measured_distance)/ real_width
    return focal_length

def distance_camera_to_face_calculator(focal_length, real_face_width, face_width_in_frame):
    distance = (real_face_width * focal_length)/face_width_in_frame
    return distance

def put_text_args(height, width, n_lines, scale):
    font_scale = int(min(width,height)/(350/scale))
    font_thickness = int(min(width,height)/500)
    # 
    line_width = int(font_thickness)
    point_width = int(font_thickness)
    thickness_oval = int(1.5*font_thickness)
    # 
    x_position_0 = int(width/20)
    top_padding = height/20
    text_block_height = height*0.6
    line_heigh_increase = text_block_height/n_lines
    y_position_v = [top_padding]
    for i in range(1,n_lines):
        y_position_temp = int(y_position_v[i-1] + line_heigh_increase)
        y_position_v.append(y_position_temp)
    # 
    return font_scale, font_thickness, line_width, point_width, thickness_oval, x_position_0, y_position_v

# ---------------------------------
# IMAGE PROCESSING TOOLS
# ---------------------------------

def bgr_image(image):
    """ The code takes in an image as input and splits it into three colors: 
    blue (B), green (G), and red (R)."""
    (B, G, R) = cv2.split(image)
    return B, G, R

def height_width_image(image):
    """ The code will return the height and width of an image."""
    height, width, _ = image.shape
    return height, width

def image_bgr_to_rgb(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def image_rgb_to_bgr(image):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image

def extract_exif_metadata(image_path):
    try:
        img = Image.open(image_path)
        exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS }
        return exif
    except Exception as e: print(e), print("Check if EXIF data is availible for this image.")

def focal_length_metadata(image_path):
    focal_length = 0
    focal_length_in_35mm_film = 0
    try:
        exif = extract_exif_metadata(image_path)
        focal_length = exif['FocalLength']
        focal_length_in_35mm_film = exif['FocalLengthIn35mmFilm']
    except Exception as e: 
        print(e), print("Check if EXIF data is availible for this image.")
    # 
    return focal_length, focal_length_in_35mm_film


# ---------------------------------
# FACE LANDMARKS
# --------------------------------- 

def face_mesh_points(image):
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5)
    result = face_mesh.process(image)
    height, width = height_width_image(image)
    mesh_points= np.array([np.multiply([p.x, p.y], [width, height]).astype(int) for p in result.multi_face_landmarks[0].landmark])
    return result, mesh_points

def find_iris_location(mesh_points,landmarks):
    (l_cx, l_cy), l_radius = cv2.minEnclosingCircle(mesh_points[landmarks['rightEyeIris']])
    (r_cx, r_cy), r_radius = cv2.minEnclosingCircle(mesh_points[landmarks['leftEyeIris']])
    center_left_iris = np.array([l_cx, l_cy], dtype=np.int32)
    center_right_iris = np.array([r_cx, r_cy], dtype=np.int32)
    iris_position = [center_left_iris,center_right_iris]
    iris_radius = [l_radius, r_radius]
    # 
    return iris_position, iris_radius

# ---------------------------------
# INTERACTIVE PLOTTTIN - FACE LANDMARKS 
# --------------------------------- 

def mesh_points_to_df(mesh_points):
    df_mesh_points = pd.DataFrame(columns=['X_pos', 'Y_pos', 'idx'])
    # points_x = [mesh_points[0] for stacked_array in mesh_points]
    # points_y = [mesh_points[1] for stacked_array in mesh_points]
    for i, point in enumerate(mesh_points):
        point_x = point[0]
        point_y = point[1]
        df_mesh_points.at[i,'X_pos'] = point_x
        df_mesh_points.at[i,'Y_pos'] = point_y
        df_mesh_points.at[i,'idx'] = i
    return df_mesh_points

def mesh_points_interactive_plot(mesh_points):
    df_mesh_points = mesh_points_to_df(mesh_points)
    fig = px.scatter(df_mesh_points, y="Y_pos", x="X_pos",hover_data=['idx'])
    fig.update_traces(marker_size=5)
    fig['layout']['yaxis']['autorange'] = "reversed"
    fig.write_html("output/landmarks_mesh.html")
    return fig

def mesh_points_interactive_plot_with_image(mesh_points, image_path):
    image_temp = cv2.imread(image_path)
    df_mesh_points = mesh_points_to_df(mesh_points)
    height, width = height_width_image(image_temp)
    # 
    fig = go.Figure()
    fig.add_layout_image(
            x=0,
            sizex=width,
            y=0,
            sizey=height,
            xref="x",
            yref="y",
            opacity=1.0,
            layer="below",
            source=image_path
    )
    fig.add_scatter(x=df_mesh_points['X_pos'],y=df_mesh_points['Y_pos'],mode="markers",marker=dict(size=1, color="Red"))
    fig.update_xaxes(showgrid=False, range=(0, width))
    fig.update_yaxes(showgrid=False, scaleanchor='x', range=(height, 0))
    fig.update_layout(xaxis_range=[0,width])
    fig.write_html("output/landmarks_mesh_with_photo.html")
    fig.write_image("output/landmarks_mesh_with_photo.png")
    fig.write_image("output/landmarks_mesh_with_photo.svg")
    fig.write_image("output/landmarks_mesh_with_photo.pdf")
    return fig

# ---------------------------------
# MEASUREMENTS FACE LANDMARKS
# --------------------------------- 

def get_face_dimensions_px(mesh_points, landmarks):
    width_face_px = distanceCalculate(mesh_points[landmarks['leftToRight']])
    height_face_px = distanceCalculate(mesh_points[landmarks['topToBottom']])
    return width_face_px, height_face_px

def get_ipd_px(iris_position):
    center_left_iris = iris_position[0]
    center_right_iris = iris_position[1]
    ipd_px = distanceCalculate([center_left_iris, center_right_iris])
    return ipd_px

def area_px_right_silhoutte_calc(mesh_points, landmarks):
    right_silhoutte = mesh_points[landmarks['rightSilhouette']]
    area_px_right_silhoutte = area_px_within_polyline(right_silhoutte)
    return area_px_right_silhoutte

def area_px_left_silhoutte_calc(mesh_points, landmarks):
    left_silhoutte = mesh_points[landmarks['leftSilhouette']]
    area_px_left_silhoutte = area_px_within_polyline(left_silhoutte)
    return area_px_left_silhoutte

def get_top_to_bottom_angle(mesh_points, landmarks):
    top_to_bottom_angle = angleLinePoints(mesh_points[landmarks['topToBottom']])
    return top_to_bottom_angle

def get_left_to_right_angle(mesh_points, landmarks):
    left_to_right_angle = angleLinePoints(mesh_points[landmarks['leftToRight']])
    return left_to_right_angle

def get_left_cheek_to_nose_angle(mesh_points, landmarks):
    left_to_right_angle = angleLinePoints(mesh_points[landmarks['leftCheekToNose']])
    return left_to_right_angle

def get_nose_to_right_cheek_angle(mesh_points, landmarks):
    left_to_right_angle = angleLinePoints(mesh_points[landmarks['noseToRightCheek']])
    return left_to_right_angle


# ---------------------------------
# DRAW LANDMARKS
# --------------------------------- 
colour_line = (255, 0, 0)
colour_point = (255, 0, 0)
colour_rectangle = (255, 255, 255)
colour_oval = (255, 255, 255)
colour_point_iris = (0, 255, 0)

def print_face_mesh_image(image, result):
    height, width = height_width_image(image)
    for facial_landmarks in result.multi_face_landmarks:
        for i in range(0, 468):
            pt1 = facial_landmarks.landmark[i]
            x = int(pt1.x * width)
            y = int(pt1.y * height)
            image = cv2.circle(image, (x, y), 1, colour_point, point_width)
    return image


def print_iris_location(image, mesh_points, landmarks):
    image = cv2.polylines(image, [mesh_points[landmarks['rightEyeIris']]], 1, colour_line, line_width)
    image = cv2.polylines(image, [mesh_points[landmarks['leftEyeIris']]], 1, colour_line, line_width)
    return image

def print_center_iris(image, iris_position):
    center_left_iris = iris_position[0]
    center_right_iris = iris_position[1]
    image = cv2.circle(image, center_left_iris, 1, colour_point_iris, 10*point_width)
    image = cv2.circle(image, center_right_iris, 1, colour_point_iris, 10*point_width)
    return image

def print_line_left_to_right_iris(image, iris_position):
    center_left_iris = iris_position[0]
    center_right_iris = iris_position[1]
    image = cv2.line(image, center_left_iris, center_right_iris, colour_line, line_width)
    # 
    return image

def print_line_top_to_bottom(image, mesh_points, landmarks):
    image = cv2.polylines(image, [mesh_points[landmarks['topToBottom']]],  1, colour_line, line_width)
    return image

def print_line_left_to_right(image, mesh_points, landmarks):
    image = cv2.polylines(image, [mesh_points[landmarks['leftToRight']]],  1, colour_line, line_width)
    return image

def print_line_left_cheek_to_nose(image, mesh_points, landmarks):
    image = cv2.polylines(image, [mesh_points[landmarks['leftCheekToNose']]],  1, colour_line, line_width)
    return image

def print_line_nose_to_right_cheek(image, mesh_points, landmarks):
    image = cv2.polylines(image, [mesh_points[landmarks['noseToRightCheek']]],  1, colour_line, line_width)
    return image

def print_silhouette(image, mesh_points, landmarks):
    image = cv2.polylines(image, [mesh_points[landmarks['silhouette']]],  1, colour_line, line_width)
    return image

def print_right_silhouette(image, mesh_points, landmarks):
    image = cv2.polylines(image, [mesh_points[landmarks['rightSilhouette']]],  1, colour_line, line_width)
    return image

def print_left_silhouette(image, mesh_points, landmarks):
    image = cv2.polylines(image, [mesh_points[landmarks['leftSilhouette']]],  1, colour_line, line_width)
    return image

def print_rectangle_card_area(image, mesh_points, landmarks):
    _, height_face_px = get_face_dimensions_px(mesh_points, landmarks)
    x_start = mesh_points[landmarks['outerRightEyebrowUpper']][0]
    y_start = mesh_points[landmarks['outerRightEyebrowUpper']][1] - 0.6*height_face_px
    x_end, y_end =  mesh_points[landmarks['outerLeftEyebrowUpper']]
    start_point = (int(x_start), int(y_start))
    end_point = (int(x_end), int(y_end))
    image = cv2.rectangle(image, start_point, end_point, colour_rectangle, line_width)
    return image

def print_face_oval(image):
    height, width = height_width_image(image)
    image = cv2.ellipse(image, center=(int(width/2), int(height/2)), axes=(int(min(width,height)/4),int(min(width,height)/3)), angle=0, startAngle=0, endAngle=360, color=colour_oval, thickness=thickness_oval)  
    return image

# ---------------------------------
# SCREEN-PRINTING
# ---------------------------------

# Printing text information onscreen
colour_text =  (255, 255, 0)
colour_text_valid = (0,255,0)
colour_text_invalid = (255, 0, 0)
# 

def screenprint_top_to_bottom_angle(image, top_to_bottom_angle, top_to_bottom_angle_ref, top_to_bottom_angle_max_deviation):
    if abs(top_to_bottom_angle - top_to_bottom_angle_ref) < top_to_bottom_angle_max_deviation:
        colour_text_top_to_bottom_angle = colour_text_valid
    else:
        colour_text_top_to_bottom_angle = colour_text_invalid
    image = cv2.putText(image, f'top_to_bottom_angle: {str(round(top_to_bottom_angle,3))} [degrees]', (int(x_position_0),int(y_position_v[0])), cv2.FONT_HERSHEY_PLAIN, font_scale, colour_text_top_to_bottom_angle, font_thickness)
    return image

def screenprint_left_to_right_angle(image, left_to_right_angle, left_to_right_angle_ref, left_to_right_angle_max_deviation_perc):
    if abs(left_to_right_angle - left_to_right_angle_ref) < left_to_right_angle_max_deviation_perc:
        colour_text_left_to_right_angle = colour_text_valid
    else:
        colour_text_left_to_right_angle = colour_text_invalid
    image = cv2.putText(image, f'left_to_right_angle: {str(round(left_to_right_angle,3))} [degrees]', (x_position_0,int(y_position_v[1])), cv2.FONT_HERSHEY_PLAIN, font_scale, colour_text_left_to_right_angle, font_thickness)
    return image

def screenprint_ipd_px(image, ipd_px):
    image = cv2.putText(image, f'ipd_px: {str(round(ipd_px,3))} [px]', (x_position_0,int(y_position_v[2])), cv2.FONT_HERSHEY_PLAIN, font_scale, colour_text, font_thickness)
    return image

def screenprint_area_right_to_left_silhoutte(image, area_right_to_left_silhoutte, area_ratio_right_to_left_ref, area_ratio_right_to_left_max_deviation_perc):
    if abs(area_right_to_left_silhoutte - area_ratio_right_to_left_ref) < area_ratio_right_to_left_max_deviation_perc:
        colour_text_area_right_to_left_silhoutte = colour_text_valid
    else:
        colour_text_area_right_to_left_silhoutte = colour_text_invalid
    image = cv2.putText(image, f'area_right_to_left_silhoutte: {str(round(area_right_to_left_silhoutte,3))} [%]', (x_position_0,int(y_position_v[3])), cv2.FONT_HERSHEY_PLAIN, font_scale,colour_text_area_right_to_left_silhoutte, font_thickness)
    return image

def screenprint_nose_to_cheek(image,left_cheek_to_nose_angle,nose_to_right_cheek_angle):
    image = cv2.putText(image, f'Nose-Cheek Angles: {str(round(left_cheek_to_nose_angle,3)), str(round(nose_to_right_cheek_angle,3))} [degrees]', (x_position_0,int(y_position_v[4])), cv2.FONT_HERSHEY_PLAIN, font_scale,colour_text, font_thickness)
    return image


# ---------------------------------
# MAIN FUNCTION
# ---------------------------------


def process_image(image, landmarks, top_to_bottom_angle_ref, top_to_bottom_angle_max_deviation, left_to_right_angle_ref, left_to_right_angle_max_deviation_perc, area_ratio_right_to_left_max_deviation_perc, area_ratio_right_to_left_ref):
    # 
    image = image_bgr_to_rgb(image)
    # Properties of lines
    global font_scale, font_thickness, line_width, point_width, thickness_oval, x_position_0, y_position_v
    n_lines = 5
    scale = 1
    height, width = height_width_image(image)
    font_scale, font_thickness, line_width, point_width, thickness_oval, x_position_0, y_position_v = put_text_args(height, width, n_lines, scale)
    # Getting face lanmarks + iris position
    result, mesh_points = face_mesh_points(image)
    iris_position, iris_radius = find_iris_location(mesh_points,landmarks)
    # Measuring properties
    ipd_px = get_ipd_px(iris_position)
    width_face_px, height_face_px = get_face_dimensions_px(mesh_points, landmarks)
        # distance_camera_to_face = distance_camera_to_face_calculator(focal_length, real_face_width, width_face_px)
    top_to_bottom_angle = get_top_to_bottom_angle(mesh_points, landmarks)
    left_to_right_angle = get_left_to_right_angle(mesh_points, landmarks)
    left_cheek_to_nose_angle = get_left_cheek_to_nose_angle(mesh_points, landmarks)
    nose_to_right_cheek_angle = get_nose_to_right_cheek_angle(mesh_points, landmarks)
    area_px_left_silhoutte = area_px_left_silhoutte_calc(mesh_points, landmarks)
    area_px_right_silhoutte = area_px_right_silhoutte_calc(mesh_points, landmarks)
    area_right_to_left_silhoutte = (1 - (area_px_right_silhoutte/area_px_left_silhoutte))*100
    # Printing objects
    image = print_face_mesh_image(image, result)
    image = print_iris_location(image, mesh_points, landmarks)
    image = print_center_iris(image, iris_position)
    image = print_line_left_to_right_iris(image, iris_position)
    image = print_line_top_to_bottom(image, mesh_points, landmarks)
    image = print_line_left_to_right(image, mesh_points, landmarks)
    image = print_line_left_cheek_to_nose(image, mesh_points, landmarks)
    image = print_line_nose_to_right_cheek(image, mesh_points, landmarks)
    image = print_silhouette(image, mesh_points, landmarks)
    image = print_rectangle_card_area(image, mesh_points, landmarks)
    image = print_right_silhouette(image, mesh_points, landmarks)
    image = print_left_silhouette(image, mesh_points, landmarks)
    image = print_face_oval(image)
    # Screenprinting data and checks
    # 
    image = screenprint_top_to_bottom_angle(image, top_to_bottom_angle, top_to_bottom_angle_ref, top_to_bottom_angle_max_deviation)
    image = screenprint_left_to_right_angle(image, left_to_right_angle, left_to_right_angle_ref, left_to_right_angle_max_deviation_perc)
    image = screenprint_area_right_to_left_silhoutte(image, area_right_to_left_silhoutte, area_ratio_right_to_left_ref, area_ratio_right_to_left_max_deviation_perc)
    image = screenprint_ipd_px(image, ipd_px)
    image = screenprint_nose_to_cheek(image,left_cheek_to_nose_angle,nose_to_right_cheek_angle)
    # 
    return image