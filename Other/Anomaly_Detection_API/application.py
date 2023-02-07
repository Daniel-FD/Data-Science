from flask import Flask, request,jsonify, make_response
from joblib import load
# from pyod.models.iforest import IForest
import os
from flask_cors import CORS


# os.system("pipreqs . --force")
model = load('anomaly_model.joblib')

def wd_height_anomaly_detector(height, working_distance, gender):
    # 
    gender_map = {'Male': 0, 'Female': 1, 'Prefer not to say': 2} 
    data = [[int(height), int(working_distance), int(gender_map.get(gender, None))]]
    # 
    outlier = model.predict(data)[0]
    score = model.decision_function(data)[0]
    # 
    if outlier == 0 :
        valid = True
        message = "SAMPLE MESSAGE: Measurements seem normal. Customer is allowed to continue"
    elif outlier == 1 :
        valid = False
        message = 'SAMPLE MESSAGE: Outlier detected. Please double check working distance [in milimiters]. Please also check that you have added height correctly [and in centimeters]. If you believe this info is correct, please emial thomas@bryant.dental'
    # 
    return valid, message

application = Flask(__name__)
# CORS(application)

# /wd_height_anomaly_detector?working_distance=500.1&height=180.3&gender=Male
@application.route('/wd_height_anomaly_detector',methods=['GET', 'POST'])
def is_working_distance_within_normal():
    # 
    working_distance = request.args.get('working_distance', default = None, type = float)
    height = request.args.get('height', default = None, type = float)
    gender = request.args.get('gender', default = None, type = str)
    valid, message = wd_height_anomaly_detector(height, working_distance, gender)
    response = jsonify({'valid': valid, 'message': message, 'working distance': working_distance, 'height': height, 'gender': gender}), 200  # return data and 200 OK code
    resp = make_response(response)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# def lambda_handler(event, context):
#     # 
#     working_distance = event['working_distance']
#     height = event['height']
#     gender = event['gender']
#     valid, message = wd_height_anomaly_detector(height, working_distance, gender)
    

#     return {'valid': valid, 'message': message, 'working distance': working_distance, 'height': height, 'gender': gender}  # return data and 200 OK code



@application.route('/',methods=['GET'])
def doc():
    docs = ('This is an API that allows to perfrom a security check to ensure the working distance [mm] and height [cm] are within a normal range.' 
    + 'If it is not within a normal range, the app will return valid = False ' 
    + '-> that can be used to trigger an alert to the customer')
    return {'Docs' : docs}, 200

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080)
    # application.run(debug = True)