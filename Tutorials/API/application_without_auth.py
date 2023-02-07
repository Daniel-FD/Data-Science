from flask import Flask, request

# pipreqs .
def function(input_1, input_2):
    output =  input_1 + input_2
    return output

application = Flask(__name__)

@application.route('/api',methods=['GET']) # /api?input_1=3&input_2=5
def api_main():
    # 
    input_1 = request.args.get('input_1', default = None, type = int)
    input_2 = request.args.get('input_2', default = None, type = int)
    output = function(input_1, input_2)
    return { 'output': output, 'input_1': input_1, 'input_2': input_2,}, 200 

@application.route('/',methods=['GET'])
def doc():
    docs = ('This is sample API that calculates the sum of two numbers')
    return {'Docs' : docs}, 200

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=4000)
    application.run(debug = True)