docker-build-mapper:
	cp -r ../custom_mappers mapper/
	docker build -t ${IMAGE_TAG} -f mapper/infrastructure/Dockerfile mapper
	rm -f mapper/custom_mappers

docker-run-mapper:
	docker run -d --name os-ngd-building-mapper -e BOOTSTRAP_SERVERS=${BOOTSTRAP_SERVERS} -e KAFKA_SECURITY_PROTOCOL=${KAFKA_SECURITY_PROTOCOL} -e KAFKA_SASL_MECHANISM=${KAFKA_SASL_MECHANISM} -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e SOURCE_TOPIC=${SOURCE_TOPIC} -e SOURCE_TOPIC_GROUP_ID=${SOURCE_TOPIC_GROUP_ID} -e TARGET_TOPIC=${TARGET_TOPIC} -e LOG_LEVEL=${LOG_LEVEL} -e DEBUG=${DEBUG} --network "host" ${IMAGE_TAG}

docker-build-projector:
	cp -r ../custom_projectors projector/
	cp ../generic-projector/postgres_projector_template.py projector/
	docker build -t ${IMAGE_TAG} -f projector/infrastructure/Dockerfile projector
	rm -r projector/custom_projectors
	rm projector/postgres_projector_template.py

docker-run-projector:
	docker run -d --name os-ngd-building-projector -e BOOTSTRAP_SERVERS=${BOOTSTRAP_SERVERS} -e KAFKA_SECURITY_PROTOCOL=${KAFKA_SECURITY_PROTOCOL} -e KAFKA_SASL_MECHANISM=${KAFKA_SASL_MECHANISM} -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e SOURCE_TOPIC=${SOURCE_TOPIC} -e SOURCE_TOPIC_GROUP_ID=${SOURCE_TOPIC_GROUP_ID} -e DB_HOST=${DB_HOST} -e DB_PORT=${DB_PORT} -e DB_USERNAME=${DB_USERNAME} -e DB_PASSWORD=${DB_PASSWORD} -e DB_NAME=${DB_NAME} -e LOG_LEVEL=${LOG_LEVEL} -e DEBUG=${DEBUG} --network "host" ${IMAGE_TAG}
