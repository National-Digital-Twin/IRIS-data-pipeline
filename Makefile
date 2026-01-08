sonarqube-up:
	docker run -d -p 9000:9000 -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true --name sonarqube sonarqube:25.1.0.102122-community
run-sonar-scan:
	docker run \
		--rm \
		--network="host" \
		-v ${PWD}/${REPOSITORY}:/usr/src \
		-e SONAR_HOST_URL="http://localhost:9000" \
		-e SONAR_SCANNER_OPTS="-Dsonar.projectKey=${SONAR_PROJECT_KEY} -Dsonar.sources=${SOURCE_CODE_DIR} -Dsonar.tests=${TEST_DIR}" \
		-e SONAR_TOKEN="${SONAR_TOKEN}" \
		sonarsource/sonar-scanner-cli
developer-resources-up:
	(MINIO_ROOT_USER=$(MINIO_ROOT_USER) MINIO_ROOT_PASSWORD=$(MINIO_ROOT_PASSWORD) docker compose -f developer_resources/docker-compose.yaml -d up)
developer-resources-down:
	docker compose -f developer_resources/docker-compose.yaml down
