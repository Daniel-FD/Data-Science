from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

# pipreqs .
def function(input_1, input_2):
    output =  input_1 + input_2
    return output

application = Flask(__name__)

# Auth
auth = HTTPBasicAuth()
users = {
    "daniel": generate_password_hash("daniel-bd"),
    "tom": generate_password_hash("tom-bd")
}
@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username
#
# curl -u daniel:daniel-bd -i -X GET "http://10.0.0.160:4000/api?input_1=3&input_2=5"
@application.route('/api',methods=['GET']) # /api?input_1=3&input_2=5
@auth.login_required
def api_main():
    # 
    input_1 = request.args.get('input_1', default = None, type = int)
    input_2 = request.args.get('input_2', default = None, type = int)
    output = function(input_1, input_2)
    print(output)
    return { 'output': output, 'input_1': input_1, 'input_2': input_2,}, 200 

# curl -u daniel:daniel-bd -i -X GET http://10.0.0.160:4000/
@application.route('/',methods=['GET'])
def doc():
    docs = ('This is sample API that calculates the sum of two numbers. Sample call: # curl -u username:password -i -X GET \'http://10.0.0.160:4000/api?input_1=3&input_2=5\'.')
    return {'Docs' : docs}, 200

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=4000)
    application.run(debug = True)