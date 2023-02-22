# 1. Initialize your EB CLI repository with the eb init command:
eb init
# eb init --region eu-east-1 ...

# 2. Create an environment and deploy your application to it with eb create:
eb create 

# 3. When the environment creation process completes, open your web site with eb open:
eb open

# [] For re-deploying
# cd path/to/file
# env_name = 'qr-sensor-clinical-trial-env'
# eb deploy {env_name}
eb deploy qr-sensor-clinical-trial-env

# Other commands
eb status
eb health

