docker-build:
	docker build -t address-profile-mapper -f infrastructure/Dockerfile .

docker-run:
	docker run --rm --name address-profile-mapper -e BOOTSTRAP_SERVERS=localhost:9092 -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e SOURCE_TOPIC=address-profile -e TARGET_TOPIC=knowledge -e FILENAME=${FILE_NAME} --network "host" address-profile-mapper