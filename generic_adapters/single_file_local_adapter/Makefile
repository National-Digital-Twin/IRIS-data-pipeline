docker-build:
	docker build -t generic-adapter --build-arg SOURCE_FILE=${SOURCE_FILE} -f infrastructure/Dockerfile .

docker-run:
	docker run -d --name generic-adapter -e BOOTSTRAP_SERVERS=localhost:9092 -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e PRODUCER_NAME=${PRODUCER_NAME} -e SOURCE_NAME=epc -e TARGET_TOPIC=${TARGET_TOPIC} -e FILENAME=${FILE_NAME} -e LIMIT=0 --network "host" generic-adapter
