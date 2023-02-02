from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

webhook_url_0 = 'https://hooks.zapier.com/hooks/catch/1864978/3ybl903/'

def webhook_creation_and_call(stage, uniqueID):
    data = {'UniqueID': str(uniqueID), 'Stage': str(stage)}
    print(data)
    requests.post(webhook_url_0, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    return "Webhook sent"

# http://127.0.0.1:5001/?uniqueID=BD0002
@app.route("/", methods=['GET', 'POST'])

def index():
    # this doesn't work! gets overwritten when a post/get request is made
    # this unique ID needs to be obtained before
    uniqueID = request.args.get('uniqueID')
    if request.method == 'POST':
        if request.form.get('Order Ready to Send') == 'Order Ready to Send':
            stage = request.form.get('Order Ready to Send')
            webhook_creation_and_call(stage, uniqueID)
            print("Order Ready to Send")
        elif  request.form.get('In Manufacturing') == 'In Manufacturing':
            stage = request.form.get('In Manufacturing')
            webhook_creation_and_call(stage, uniqueID)
        else:
            # pass # unknown
            return render_template("index.html")
    elif request.method == 'GET':
        # return render_template("index.html")
        print("No Post Back Call")
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug = True, port = 5001)