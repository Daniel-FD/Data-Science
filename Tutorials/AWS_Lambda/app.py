import json

def lambda_handler(event, context):
  name= event["queryStringParameters"]['name']
  surname= event["queryStringParameters"]['surname']
  msg_body = "Hello " + str(name) + " " + str(surname) + ": message from Lambda!"
  print(msg_body)
  return {
                    "statusCode": 200,
                    "body": json.dumps(msg_body),
                    "headers": {
                      "content-type": "application/json"
                    }
                  }