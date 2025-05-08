docker-build:
	docker build -t lat-long-file-adapter --build-arg SOURCE_FILE=${SOURCE_FILE} -f infrastructure/Dockerfile .

docker-run:
	docker run --rm --name lat-long-file-adapter -e BOOTSTRAP_SERVERS=localhost:9092 -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e PRODUCER_NAME=address-base -e SOURCE_NAME=epc -e TARGET_TOPIC=lat-long -e FILENAME=${FILE_NAME} -e LIMIT=0 --network "host" lat-long-file-adapter
