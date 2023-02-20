from flask import Flask, render_template, request, redirect, url_for
import requests
import json
# from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField


application = Flask(__name__)
#
webhook_url_0 = 'https://hooks.zapier.com/hooks/catch/1864978/3ybl903/'
#
# http://127.0.0.1:5001/BD17110
# http://127.0.0.1:5001/?payload=%7B%22uniqueID%22%3A+%22BD17110%22%7D


@application.route("/favicon.ico", methods=['GET', 'POST'])
def favicon_redirect():
    return redirect(url_for('index'))


@application.route("/<uniqueID>", methods=['GET', 'POST'])
def get_uniqueID(uniqueID):
    uniqueID = uniqueID
    data = json.dumps({'uniqueID': uniqueID})
    return redirect(url_for('index', payload=data))


@application.route("/", methods=['GET', 'POST'])
def index():
    global uniqueID
    try:
        data = request.args['payload']
        data_json = json.loads(data)
        if data_json['uniqueID'] == 'favicon.ico':
            print("Favicon URL")
        else:
            uniqueID = data_json['uniqueID']
            print("---------")
            print(uniqueID)
            print("---------")
    except:
        print("Unique ID already retrieved!")
    #
    if request.form.get('Order Arrived') == 'Order Arrived':
        print("Button <Order Arrived> clicked!")
        stage = request.form.get('Order Arrived')
        data = json.dumps({'uniqueID': uniqueID, 'stage': stage})
        print(data)
        return redirect(url_for('send_webhook', payload=data))
    elif request.form.get('Order Assembled') == 'Order Assembled':
        print("Button <Order Assembled> clicked!")
        stage = request.form.get('Order Assembled')
        loupes_serial_number = request.form.get('Loupes Serial Number')
        halo_serial_number = request.form.get('Halo Serial Number')
        ignis_led_serial_number = request.form.get('Ignis LED Serial Number')
        ignis_battery_serial_number = request.form.get('Ignis Battery Serial Number')
        ignis_charging_plate_serial_number = request.form.get('Ignis Charging Plate Serial Number')
        print("------------------------")
        print('Stage: ', stage)
        print('Loupes Serial Number: ', loupes_serial_number)
        print('Halo Serial Number: ', halo_serial_number)
        print('Ignis LED Serial Number: ', ignis_led_serial_number)
        print('Ignis Battery Serial Number: ', ignis_battery_serial_number)
        print('Ignis Charging Plate Serial Number: ',
              ignis_charging_plate_serial_number)
        # data = json.dumps({'uniqueID': uniqueID, 'stage': stage})
        dictionary_data = {'uniqueID': str(uniqueID),
                            'stage': str(stage),
                            'loupes_serial_number': str(loupes_serial_number),
                            'halo_serial_number': str(halo_serial_number),
                            'ignis_led_serial_number': str(ignis_led_serial_number),
                            'ignis_battery_serial_number': str(ignis_battery_serial_number),
                            'ignis_charging_plate_serial_number': str(ignis_charging_plate_serial_number)}
        data = json.dumps(dictionary_data)
        print(data)
        print("------------------------")
        return redirect(url_for('send_webhook', payload=data))
    else:
        return render_template("index.html")


@application.route("/success", methods=['GET', 'POST'])
def send_webhook():
    data_temp = request.args['payload']
    data_json = json.loads(data_temp)
    # 
    stage = data_json['stage']
    uniqueID = data_json['uniqueID']
    if stage == 'Order Assembled':
        loupes_serial_number = data_json['loupes_serial_number']
        halo_serial_number = data_json['halo_serial_number']
        ignis_led_serial_number = data_json['ignis_led_serial_number']
        ignis_battery_serial_number = data_json['ignis_battery_serial_number']
        ignis_charging_plate_serial_number = data_json['ignis_charging_plate_serial_number']
        # 
        query_string = ('?UniqueID=' + str(uniqueID) + '&stage=' + str(stage)
                        + '&loupes_serial_number=' + str(loupes_serial_number) 
                        + '&halo_serial_number=' + str(halo_serial_number) 
                        + '&ignis_led_serial_number=' + str(ignis_led_serial_number) 
                        + '&ignis_battery_serial_number=' + str(ignis_battery_serial_number) 
                        + '&ignis_charging_plate_serial_number=' + str(ignis_charging_plate_serial_number))
    elif stage == 'Order Arrived':
        query_string = ('?UniqueID=' + str(uniqueID) + '&stage=' + str(stage))
    #
    print("------------------------")
    print(query_string)
    print("Sending webhook....")
    print("------------------------")
    r = requests.post(webhook_url_0 + query_string, data=json.dumps(data_json),headers={'Content-Type': 'application/json'})
    #
    
    return render_template("webhook_sent.html")


if __name__ == '__main__':
    application.run(debug=True, port=5001)
