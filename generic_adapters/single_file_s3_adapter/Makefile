docker-build:
	docker build -t address-profile-s3-file-adapter -f infrastructure/Dockerfile .

docker-run:
	docker run --rm --name address-profile-s3-file-adapter -e BOOTSTRAP_SERVERS=localhost:9092 -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e PRODUCER_NAME=address-profile -e SOURCE_NAME=epc -e TARGET_TOPIC=address-profile -e S3_BUCKET=${BUCKET_NAME} -e S3_FILENAME=${FILE_NAME} -e DEFAULT_SECURITY_LABEL=${DEFAULT_SECURITY_LABEL} --network "host" address-profile-s3-file-adapter