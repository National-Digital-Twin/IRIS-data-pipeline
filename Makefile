start-local-zookeeper:
	/opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties
start-local-kafka:
	/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
start-kafka-docker:
	docker compose up -d
stop-and-remove-kafka-docker:
	docker compose down