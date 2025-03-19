docker-build:
	docker build -t lat-long-mapper -f infrastructure/Dockerfile .

docker-run:
	docker run --rm --name lat-long-mapper -e BOOTSTRAP_SERVERS=localhost:9092 -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e SOURCE_TOPIC=lat-long -e SOURCE_TOPIC_GROUP_ID=lat-long -e TARGET_TOPIC=knowledge --network "host" lat-long-mapper