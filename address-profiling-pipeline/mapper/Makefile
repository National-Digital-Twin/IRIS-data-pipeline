docker-build:
	cp -r ../../custom_mappers/ ./
	docker build -t ${IMAGE_TAG} -f infrastructure/Dockerfile .
	rm -rf custom_mappers

docker-run:
	docker run -d --name ${IMAGE_TAG} -e BOOTSTRAP_SERVERS=localhost:9092 -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e SOURCE_TOPIC=address-profile -e TARGET_TOPIC=knowledge -e MAP_FUNC=${MAP_FUNC} --network "host" address-profile-mapper
