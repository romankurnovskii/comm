python -m venv env
. env/bin/activate


set env:
MONGO_CONNECTION_STRING
MONGO_DB_COLLECTION

pip install -r requirements.txt
pip freeze > requirements.txt


export FLASK_APP=server
export FLASK_ENV=development
flask run

docker pull mongo:5.0.9

docker run -d --rm  --name test-mongo mongo:5.0.9 --port 8000
docker exec -it <CONTAINER_NAME> bash
docker logs test-mongo --follow


docker run -d \
    -p 27017:27017 \
    --name test-mongo \
    -v data-vol:/data/db \
    mongo

docker run -d --network my-network --name mylocalmongo \
	-e MONGO_INITDB_ROOT_USERNAME=mongoadmin \
	-e MONGO_INITDB_ROOT_PASSWORD=secret \
	mongo:5.0.9


docker run -it --rm --network mynetwork mongo \
	mongo --host some-mongo \
		-u mongoadmin \
		-p secret \
		--authenticationDatabase admin \
		some-db


docker exec -it some-mongo bash
docker logs some-mongo
