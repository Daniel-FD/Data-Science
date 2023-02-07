pipreqs --force .
rm -r aws_deployment
mkdir aws_deployment
cp requirements.txt  aws_deployment/
cp application.py aws_deployment/
cd aws_deployment
eb init -p python-3.8 test-application-aws --region us-east-1
rm -r .elasticbeanstalk
eb init
eb create test-application-aws-env
eb open test-application-aws-env
