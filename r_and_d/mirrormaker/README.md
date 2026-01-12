# Kafka MirrorMaker2 (MM2)

MM2 is a tool used to mirror Kafka data between Kafka clusters. Within this directory is code which enables you to build an mm2 image which can connect to two Kafka instances and specify which topics you'd like transferred from one to the other. At the moment, this is uni-directional and data can only be mirrored from your Kafka A cluster to your Kafka B cluster. 

## Prerequisites

To run mm2, you need two Kafka clusters. If running locally, you can start a second Kafka cluster using the docker-compose.yml file in the mirrormaker directory which will start a Kafka and Zookeeper instance in a distinct network. 

## Build the image

To build the image, run the following from within the mirrormaker directory:
`docker build -t mm2-task:latest -f Dockerfile  .`

## Run the container

To run the image as a container, run the following:
```
docker run -d \
  --network developer-resources_default \
  --mount type=bind,src="$(pwd)/mm2.properties",dst=/etc/mm2.properties,ro \
  --mount type=bind,src="$(pwd)/connect-log4j.properties",dst=/etc/kafka/connect-log4j.properties,ro \
  mm2-task:latest


docker network connect kafka_b_net mm2-task
```