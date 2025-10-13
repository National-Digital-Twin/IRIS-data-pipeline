prepare-context:
	mkdir -p infrastructure/docker-context
	cp -r ../../generic_projectors ./infrastructure/docker-context/generic_projectors
docker-build:
	docker build --secret id=pat_token,env=GITHUB_ACCESS_TOKEN -t address-profiling-projector --no-cache -f infrastructure/Dockerfile .
docker-run:
	docker run --rm --name ngd-property-projector -e DB_HOST=${DB_HOST} -e DB_PORT=${DB_PORT} -e DB_USERNAME=${DB_USERNAME} -e DB_PASSWORD=${DB_PASSWORD} -e DB_NAME=${DB_NAME} -e BOOTSTRAP_SERVERS=${BOOTSTRAP_SERVERS} -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e SOURCE_TOPIC=${SOURCE_TOPIC} -e SOURCE_TOPIC_GROUP_ID=${SOURCE_TOPIC_GROUP_ID} --network "host" address-profiling-projector