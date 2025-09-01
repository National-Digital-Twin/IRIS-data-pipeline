docker-build:
	docker build --secret id=pat_token,env=GITHUB_ACCESS_TOKEN -t s3-directory-adapter -f infrastructure/Dockerfile .
docker-run:
	docker run --rm --name s3-directory-adapter -e BOOTSTRAP_SERVERS=${BOOTSTRAP_SERVERS} -e PRODUCER_NAME=${PRODUCER_NAME} -e SOURCE_NAME=${SOURCE_NAME} -e TARGET_TOPIC=${TARGET_TOPIC} -e S3_BUCKET=${S3_BUCKET} -e S3_DIRECTORY=${S3_DIRECTORY} -e DEFAULT_SECURITY_LABEL=${DEFAULT_SECURITY_LABEL} --network "host" s3-directory-adapter