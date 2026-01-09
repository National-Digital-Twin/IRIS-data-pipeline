create-environment:
	python -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt

docker-build:
	cp -r ../../custom_mappers/ ./
	docker build -t ${IMAGE_TAG} -f infrastructure/Dockerfile .
	rm -rf custom_mappers

docker-run:
	docker run -d --name address-profiling-mapper -e BOOTSTRAP_SERVERS=localhost:9092 -e KAFKA_SECURITY_PROTOCOL=${KAFKA_SECURITY_PROTOCOL} -e KAFKA_SASL_MECHANISM=${KAFKA_SASL_MECHANISM} -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e SOURCE_TOPIC=${SOURCE_TOPIC} -e SOURCE_TOPIC_GROUP_ID=${SOURCE_TOPIC_GROUP_ID} -e TARGET_TOPIC=${TARGET_TOPIC} -e MAPPER_SUB_TYPE=${MAPPER_SUB_TYPE} --network "host" ${IMAGE_TAG}
test:
	pytest src/tests/ -v -s
