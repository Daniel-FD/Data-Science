import gradio as gr
from flask import Flask, Response
import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
import math
from IPython import display
# --------------------
MAX_ANGLE = 10
# --------------------
# --------------------
# --------------------
# --------------------
def distanceCalculate(p):
    p1 = p[0]
    p2 = p[1]
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    return dis
# --------------------
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
# --------------------
def process_image(image):
    if isinstance(image, str):
        image = cv2.imread(image)
    # 
    (B, G, R) = cv2.split(image)
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5)
    result = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    height, width, _ = image.shape
    mesh_points= np.array([np.multiply([p.x, p.y], [width, height]).astype(int) for p in result.multi_face_landmarks[0].landmark])
    # Landmark mapping
    landmarks = {
        'topToBottom': [10, 152],
        'leftToRight': [234, 454],
        'rightEyeIris': [473, 474, 475, 476, 477],
        'leftEyeIris': [468, 469, 470, 471, 472],
        'outerRightEyebrowUpper': 70,
        'outerLeftEyebrowUpper': 300,
        'silhouette': [10,  338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
        397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
        172, 58,  132, 93,  234, 127, 162, 21,  54,  103, 67,  109]}
    # Iris location
    (l_cx, l_cy), l_radius = cv2.minEnclosingCircle(mesh_points[landmarks['rightEyeIris']])
    (r_cx, r_cy), r_radius = cv2.minEnclosingCircle(mesh_points[landmarks['leftEyeIris']])
    center_left_iris = np.array([l_cx, l_cy], dtype=np.int32)
    center_right_iris = np.array([r_cx, r_cy], dtype=np.int32)
    # Face dimension
    width_face_px = distanceCalculate(mesh_points[landmarks['leftToRight']])
    height_face_px = distanceCalculate(mesh_points[landmarks['topToBottom']])
    # IPD calculation
    ipd = distanceCalculate([center_left_iris, center_right_iris])
    # Photo Quality Check
    vertical_angle = angleLinePoints(mesh_points[landmarks['topToBottom']])
    horizonal_angle = angleLinePoints(mesh_points[landmarks['leftToRight']])
    # Rectangle for Card Area
    x_start = mesh_points[landmarks['outerRightEyebrowUpper']][0]
    y_start = mesh_points[landmarks['outerRightEyebrowUpper']][1] - 0.6*height_face_px
    x_end, y_end =  mesh_points[landmarks['outerLeftEyebrowUpper']]
    start_point = (int(x_start), int(y_start))
    end_point = (int(x_end), int(y_end))
    # 
    overlay = image.copy()
    alpha = 0.1
    beta = (1.0 - alpha)
    # Plot all the information
    # plt.imshow(image)
    # plt.imshow(image_landmarks)
    for facial_landmarks in result.multi_face_landmarks:
        for i in range(0, 468):
            pt1 = facial_landmarks.landmark[i]
            x = int(pt1.x * width)
            y = int(pt1.y * height)
            cv2.circle(image, (x, y), 1, (0,255,0), -1)
    plt.imshow(cv2.polylines(image, [mesh_points[landmarks['topToBottom']]], 1, (0,255,0), 1))
    plt.imshow(cv2.polylines(image, [mesh_points[landmarks['leftToRight']]], 1, (0,255,0), 1))
    plt.imshow(cv2.polylines(image, [mesh_points[landmarks['silhouette']]], 1, (0,255,0), 1))
    plt.imshow(cv2.line(image, center_left_iris, center_right_iris, (0, 255, 0), 2))
    plt.imshow(cv2.line(image, mesh_points[landmarks['outerLeftEyebrowUpper']], mesh_points[landmarks['outerRightEyebrowUpper']], (0, 255, 0), 1))
    plt.imshow(cv2.rectangle(image, start_point, end_point, (255,0,0), 1))
    plt.imshow(cv2.ellipse(image, center=(int(width/2), int(height/2)), axes=(int(min(width,height)/4),int(min(width,height)/3)), angle=0, startAngle=0, endAngle=360, color=(255,255,255), thickness=4))    
    plt.imshow(cv2.putText(image, f'IPD: {str(ipd)} [px]', (50,50), cv2.FONT_HERSHEY_PLAIN,1, (0,0,0), 1))
    plt.imshow(cv2.putText(image, f'Face Height: {str(height_face_px)} [px]', (50,100), cv2.FONT_HERSHEY_PLAIN,1, (0,0,0),1))
    plt.imshow(cv2.putText(image, f'Face Width: {str(width_face_px)} [px]', (50,150), cv2.FONT_HERSHEY_PLAIN,1, (0,0,0), 1))
    if abs(horizonal_angle) < MAX_ANGLE:
        plt.imshow(cv2.putText(image, f'Horizonal Angle: {str(horizonal_angle)} [degrees]', (50,200), cv2.FONT_HERSHEY_PLAIN,1, (0,255,0), 1))
        cv2.rectangle(overlay, (0,0), (width, height), (0, 255, 0), -1)  
        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
    elif horizonal_angle < -MAX_ANGLE:
        plt.imshow(cv2.arrowedLine(image,[int(x_start) - (int(min(width,height)/4)),int(y_start+ height_face_px/2)], [int(x_start), int(y_start+ height_face_px/2)], (0, 255, 0), 4))
        plt.imshow(cv2.putText(image, f'Horizonal Angle: {str(horizonal_angle)} [degrees]', (50,200), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1))
        cv2.rectangle(overlay, (0,0), (width, height), (0, 0, 255), -1)  
        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
        plt.imshow(image)
    elif horizonal_angle > MAX_ANGLE:
        plt.imshow(cv2.arrowedLine(image, [int(x_start), int(y_start+ height_face_px/2)],[int(x_start) - (int(min(width,height)/4)),int(y_start+ height_face_px/2)], (0, 255, 0), 4))
        plt.imshow(cv2.putText(image, f'Horizonal Angle: {str(horizonal_angle)} [degrees]', (50,200), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1))
        cv2.rectangle(overlay, (0,0), (width, height), (0, 0, 255), -1)  
        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
        plt.imshow(image)
    if abs(vertical_angle) > (90 - MAX_ANGLE): #[-80, 80] -> okay
        plt.imshow(cv2.putText(image, f'Vertical Angle: {str(vertical_angle)} [degrees]', (50,250), cv2.FONT_HERSHEY_PLAIN,1, (0,255,0), 1))
    else:         
        plt.imshow(cv2.putText(image, f'Vertical Angle: {str(vertical_angle)} [degrees]', (50,250), cv2.FONT_HERSHEY_PLAIN,1, (0,0,255), 1))
    # 
    return image
# --------------------
# --------------------
# --------------------
# --------------------
def processing_frame(im):
    image = process_image(im)
    return image
# 
demo = gr.Interface(
    processing_frame, 
    gr.Image(source="webcam", streaming=True), 
    "image",
    live=True
)
demo.launch()