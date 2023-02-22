from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import numpy as np
#
webhook_url_0 = 'https://vusf88cage.execute-api.us-east-1.amazonaws.com/test'
#
application = Flask(__name__)
# ---------------------------
@application.route("/favicon.ico", methods=['GET', 'POST'])
def favicon_redirect():
    return redirect(url_for('index'))
# ---------------------------
@application.route("/<deviceID>", methods=['GET', 'POST'])
def get_deviceID(deviceID):
    deviceID = deviceID
    data = json.dumps({'deviceID': deviceID})
    return redirect(url_for('index', payload=data))
# ---------------------------
@application.route("/", methods=['GET', 'POST'])
def index():
    global deviceID
    try:
        data = request.args['payload']
        data_json = json.loads(data)
        if data_json['deviceID'] == 'favicon.ico':
            print("Favicon URL")
        else:
            deviceID = data_json['deviceID']
            print("---------")
            print(deviceID)
            print("---------")
    except: print("Unique ID already retrieved!")
    #
    if request.form.get('Positive Label') == 'Positive':
        print("Button <Positive Label> clicked!")
        label = request.form.get('Positive Label')
        data = json.dumps({'deviceID': deviceID, 'label': label})
        print(data)
        return redirect(url_for('send_webhook', payload=data))
        # 
    elif request.form.get('Negative Label') == 'Negative':
        label = request.form.get('Negative Label')
        data = json.dumps({'deviceID': deviceID, 'label': label})
        print(data)
        return redirect(url_for('send_webhook', payload=data))
    elif request.form.get('No Label') == 'No Label':
        label = np.nan
        data = json.dumps({'deviceID': deviceID, 'label': label})
        print(data)
        return redirect(url_for('send_webhook', payload=data))
    else:
        return render_template("index.html")

# ---------------------------
@application.route("/success", methods=['GET', 'POST'])
def send_webhook():
    # 
    data_temp = request.args['payload']
    data_json = json.loads(data_temp)
    # 
    label = data_json['label']
    deviceID = data_json['deviceID']
    query_string = ('?deviceID=' + str(deviceID) + '&label=' + str(label))
    #
    print("------------------------")
    print(query_string)
    print("Sending webhook....")
    print("------------------------")
    r = requests.post(webhook_url_0 + query_string, data=json.dumps(data_json),headers={'Content-Type': 'application/json'})
    print(r, r.content)
    #
    return render_template("webhook_sent.html")


if __name__ == '__main__':
    application.run(debug=True, port=5001)
