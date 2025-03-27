docker-build:
	docker build -t retrofit-ontology-adapter -f infrastructure/Dockerfile .

docker-run:
	docker run --rm --name retrofit-ontology-adapter -e BOOTSTRAP_SERVERS=localhost:9092 -e SASL_USERNAME=${SASL_USERNAME} -e SASL_PASSWORD=${SASL_PASSWORD} -e SOURCE_NAME=retrofit-ontology -e TARGET_TOPIC=ontology -e PRODUCER_NAME=retrofit-ontology --network "host" retrofit-ontology-adapter