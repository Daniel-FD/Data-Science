import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
import math
from PIL import Image


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh


landmarks = {
    'silhouette': [
    10,  338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
    172, 58,  132, 93,  234, 127, 162, 21,  54,  103, 67,  109
  ],

  'lipsUpperOuter': [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291],
  'lipsLowerOuter': [146, 91, 181, 84, 17, 314, 405, 321, 375, 291],
  'lipsUpperInner': [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308],
  'lipsLowerInner': [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308],

  'rightEyeUpper0': [246, 161, 160, 159, 158, 157, 173],
  'rightEyeLower0': [33, 7, 163, 144, 145, 153, 154, 155, 133],
  'rightEyeUpper1': [247, 30, 29, 27, 28, 56, 190],
  'rightEyeLower1': [130, 25, 110, 24, 23, 22, 26, 112, 243],
  'rightEyeUpper2': [113, 225, 224, 223, 222, 221, 189],
  'rightEyeLower2': [226, 31, 228, 229, 230, 231, 232, 233, 244],
  'rightEyeLower3': [143, 111, 117, 118, 119, 120, 121, 128, 245],

  'rightEyebrowUpper': [156, 70, 63, 105, 66, 107, 55, 193],
  'rightEyebrowLower': [35, 124, 46, 53, 52, 65],

  'rightEyeIris': [473, 474, 475, 476, 477],

  'leftEyeUpper0': [466, 388, 387, 386, 385, 384, 398],
  'leftEyeLower0': [263, 249, 390, 373, 374, 380, 381, 382, 362],
  'leftEyeUpper1': [467, 260, 259, 257, 258, 286, 414],
  'leftEyeLower1': [359, 255, 339, 254, 253, 252, 256, 341, 463],
  'leftEyeUpper2': [342, 445, 444, 443, 442, 441, 413],
  'leftEyeLower2': [446, 261, 448, 449, 450, 451, 452, 453, 464],
  'leftEyeLower3': [372, 340, 346, 347, 348, 349, 350, 357, 465],

  'leftEyebrowUpper': [383, 300, 293, 334, 296, 336, 285, 417],
  'leftEyebrowLower': [265, 353, 276, 283, 282, 295],

  'leftEyeIris': [468, 469, 470, 471, 472],

  'midwayBetweenEyes': [168],

  'noseTip': [1],
  'noseBottom': [2],
  'noseRightCorner': [98],
  'noseLeftCorner': [327],

  'rightCheek': [205],
  'leftCheek': [425]
}

def measurements_checks(image_0):

    # read image path
    try:
      image = cv2.imread(image_0)
    except: 
      image_0 = Image.fromarray(image_0, 'RGB')
      image = cv2.imread(image_0)

    # get image height and width
    img_h, img_w = image.shape[:2]

    # define face mesh object
    face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5)

    # use face mesh object to get facial landmarks
    results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    mesh_points=np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int) for p in results.multi_face_landmarks[0].landmark])

    # get indices of landmarks we want to extract (both iris and nasal bridge)
    left_iris, right_iris = landmarks['rightEyeIris'], landmarks['leftEyeIris']
    midwayBetweenEyes = landmarks['midwayBetweenEyes']

    # estimate the radius and centre of cornea
    (l_cx, l_cy), l_radius = cv2.minEnclosingCircle(mesh_points[left_iris])
    (r_cx, r_cy), r_radius = cv2.minEnclosingCircle(mesh_points[right_iris])
    
    center_left = np.array([l_cx, l_cy], dtype=np.int32)
    center_right = np.array([r_cx, r_cy], dtype=np.int32)

    # get the coordinates of the nasal bridge
    nose_bridge = mesh_points[midwayBetweenEyes][0]
    

   # calculate distance between nasal bridge and both pupils 
    distR = math.dist(center_right, nose_bridge)
    distL = math.dist(center_left, nose_bridge)
    # ipd = math.dist(center_left, center_right)

    # convert to 2 decimal places
    distL = round(distL, 2)
    distR = round(distR, 2)
    # ipd = round(ipd, 2)


    # Difference in x coordinates
    dx = center_left[0] - center_right[0]

    # Difference in y coordinates
    dy = center_left[1] - center_right[1]

    # Angle between center_left and center_right in radians
    theta = math.atan2(dy, dx)

    # convert angle from radians to degree and 2 decimal places
    degree = math.degrees(theta)
    degree = round(degree, 2)


    img = image.copy()

    # draw points and lines on image
    cv2.circle(img, center_left, int(l_radius), (255,0,255), 1, cv2.LINE_AA)
    cv2.circle(img, center_right, int(r_radius), (255,0,255), 1, cv2.LINE_AA)

    cv2.line(img, nose_bridge, center_right, (0, 0, 255), 2)
    cv2.line(img, nose_bridge, center_left, (0, 255, 0), 2)

    img = cv2.putText(img, f'Right Pupil to nose bridge: {str(distR)}', (50,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    img = cv2.putText(img, f'Left Pupil to nose bridge: {str(distL)}', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    img = cv2.putText(img, f'Angle between the two pupils: {str(degree)}', (50,70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	
    # # display image
    # plt.imshow(img)
    # plt.title('image')
    # plt.grid(False)
    # plt.show()
    # 
    return img