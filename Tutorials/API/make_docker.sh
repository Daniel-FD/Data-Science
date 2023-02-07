pipreqs .
docker image build -t flask_app .
docker run -p 5000:5000 -d flask_app
sleep 2
curl http://localhost:5000/
open http://localhost:5000/
open http://localhost:5000/api?input_1=3&input_2=5