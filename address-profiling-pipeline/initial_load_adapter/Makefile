docker-build:
	docker build -t address-profile-file-adapter --build-arg SOURCE_FILE=${SOURCE_FILE} -f infrastructure/Dockerfile .

docker-run:
	docker run -d --rm --name address-profile-file-adapter -e BOOTSTRAP_SERVERS=localhost:9092 -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e PRODUCER_NAME=address-profile -e SOURCE_NAME=epc -e TARGET_TOPIC=address-profile -e FILENAME=${FILE_NAME} -e LIMIT=0 --network "host" address-profile-file-adapter
