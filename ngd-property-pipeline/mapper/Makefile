prepare-context:
	mkdir -p infrastructure/docker-context
	cp -r ../../generic_mappers ./infrastructure/docker-context/generic_mappers
docker-build:
	docker build --secret id=pat_token,env=GITHUB_ACCESS_TOKEN -t ngd-property-mapper --no-cache -f infrastructure/Dockerfile .
docker-run:
	docker run --rm --name ngd-property-mapper -e BOOTSTRAP_SERVERS=${BOOTSTRAP_SERVERS} -e SOURCE_TOPIC=${SOURCE_TOPIC} -e SOURCE_TOPIC_GROUP_ID=${SOURCE_TOPIC_GROUP_ID} -e TARGET_TOPIC=${TARGET_TOPIC} --network "host" ngd-property-mapper