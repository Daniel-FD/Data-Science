import gradio as gr
import requests
from io import BytesIO
import base64
import matplotlib.image as mpimg
import cv2
import numpy as np

def img_to_string(img):
    # Encodes an image into a base64_string
    _, encoded_img = cv2.imencode('.PNG', img)
    base64_string = base64.b64encode(encoded_img).decode('utf-8')
    return base64_string

def string_to_img(base64_string):
    # Decodes a base64_string into an image
    imgdata = base64.b64decode(base64_string + '==')
    im = BytesIO(imgdata)
    img = mpimg.imread(im, format='PNG')
    opencv_img= cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
    return opencv_img

def api_image_processing(image):
    # API Endpoint
    url = "http://13.42.31.235/fmc_api"
    # Step 1
    b64_string = img_to_string(image)
    #  Step 2
    payload ={"base64_string": b64_string}
    response = requests.post(url=url, data=payload) 
    base64_string_resp = response.json()['message']
    # Step 3
    img_output = string_to_img(base64_string_resp)
    # Return processed image
    return img_output

demo = gr.Interface(
    api_image_processing, 
    gr.Image(source="webcam", streaming=True), 
    "image",
    live=True
)

demo.launch(debug=True)