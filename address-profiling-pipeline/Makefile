create-environment:
	python -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt

docker-build-mapper:
	cp -r ../custom_mappers/ ./
	docker build -t ${IMAGE_TAG} -f mapper/infrastructure/Dockerfile mapper
	rm -rf mapper/custom_mappers

docker-run-mapper:
	docker run -d --name address-profiling-mapper -e BOOTSTRAP_SERVERS=localhost:9092 -e KAFKA_SECURITY_PROTOCOL=${KAFKA_SECURITY_PROTOCOL} -e KAFKA_SASL_MECHANISM=${KAFKA_SASL_MECHANISM} -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e SOURCE_TOPIC=${SOURCE_TOPIC} -e SOURCE_TOPIC_GROUP_ID=${SOURCE_TOPIC_GROUP_ID} -e TARGET_TOPIC=${TARGET_TOPIC} -e MAPPER_SUB_TYPE=${MAPPER_SUB_TYPE} -e LOG_LEVEL=${LOG_LEVEL} -e DEBUG=${DEBUG} --network "host" ${IMAGE_TAG}

test-mapper:
	pytest src/tests/ -v -s

docker-build-projector:
	cp -r ../custom_projectors/ ./projector
	cp -r ../generic-projector/postgres_projector_template.py ./projector
	docker build -t ${IMAGE_TAG} -f projector/infrastructure/Dockerfile projector
	rm -rf projector/custom_projectors
	rm projector/postgres_projector_template.py

docker-run-projector:
	docker run -d --name address-profiling-projector -e BOOTSTRAP_SERVERS=localhost:9092 -e KAFKA_SECURITY_PROTOCOL=${KAFKA_SECURITY_PROTOCOL} -e KAFKA_SASL_MECHANISM=${KAFKA_SASL_MECHANISM} -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e SOURCE_TOPIC=${SOURCE_TOPIC} -e SOURCE_TOPIC_GROUP_ID=${SOURCE_TOPIC_GROUP_ID} -e DB_HOST=${DB_HOST} -e DB_PORT=${DB_PORT} -e DB_NAME=${DB_NAME} -e DB_USERNAME=${DB_USERNAME} -e DB_PASSWORD=${DB_PASSWORD} -e LOG_LEVEL=${LOG_LEVEL} -e DEBUG=${DEBUG} --network "host" ${IMAGE_TAG}

docker-build-heating-projector:
	cp -r ../custom_projectors/ ./heating-projector
	docker build -t ${IMAGE_TAG} -f heating-projector/infrastructure/Dockerfile heating-projector
	rm -rf heating-projector/custom_projectors

docker-run-heating-projector:
	docker run -d --name address-profiling-heating-projector -e BOOTSTRAP_SERVERS=localhost:9092 -e KAFKA_SECURITY_PROTOCOL=${KAFKA_SECURITY_PROTOCOL} -e KAFKA_SASL_MECHANISM=${KAFKA_SASL_MECHANISM} -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e SOURCE_TOPIC=${SOURCE_TOPIC} -e SOURCE_TOPIC_GROUP_ID=${SOURCE_TOPIC_GROUP_ID} -e SAG_ENDPOINT=${SAG_ENDPOINT} -e SAG_UPDATE_FREQUENCY=${SAG_UPDATE_FREQUENCY} -e HEATING_GRAPH_URI=${HEATING_GRAPH_URI} -e LOG_LEVEL=${LOG_LEVEL} -e DEBUG=${DEBUG} --network "host" ${IMAGE_TAG}
