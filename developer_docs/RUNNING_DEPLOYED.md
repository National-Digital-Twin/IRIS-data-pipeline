# Running in a deployed environment

## Cloud instance specification

- Memory optimized instance
- 128 GiB ram
- 500 GiB SSD
- 16 vCPUs

## Prerequisites

Please make sure you have a local instance of a GeoSPARQL enabled secure agent graph running with kafka.

To do this navigate to the `developer_resources` directory and follow the steps below:

- Ensure the cloud instance has permissions to access the private ECR image for the GeoSPARQL enabled secure agent graph.
- Authenticate aws with docker using the command `aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com`.
- Run the command `docker build -t iris-pipeline/secure-agent-graph .` to build the secure agent graph image.
- Edit the `server.properties` file found under the `kafka` folder and replace the `<host-ip>` with the internal IP of the container.
- Run the command `docker compose up -d` to run the containers for both kafka and the secure agent graph.

## Address profiling pipeline

The address profiling pipeline has two parts, the mapper and the adapter.

### Adapter

Please follow the instructions outlined in the [README.md](../generic-adapter/README.md) file to run the adapter in a deployed environment.

### Mapper

The mapper can be found under the `address-profiling-pipeline/mapper` folder. The mapper can be run as a docker container. You must build the docker container using the command `make docker-build IMAGE_TAG="address-profiling-mapper"`.
Once the container has been built use the command `make docker-run SASL_USERNAME=<insert-sasl-username> SASL_PASSWORD=<insert-sasl-password> SOURCE_TOPIC=<address-profiling-source-topic> SOURCE_TOPIC_GROUP_ID=<id-to-use-for-the-source-topic-consumer-group> TARGE_TOPIC=<topic-to-stream-mapped-records-to> MAPPER_SUB_TYPE=<sub-type-of-the-mapper-one-of[STRUCTURE_UNIT, EPC_ASSESSMENT, FLOOR, ROOF, WALL, WINDOW, HEATING]>`. The current choices for mapping function are:

- "STRUCTURE_UNIT": creates triples which are a representation of the structure unit of the dwelling
- "EPC_ASSESSMENT": creates triples which are a represenation of the epc assessment conducted for the dwelling
- "FLOOR": creates triples which are a representation of the floor details within the epc assessment of the dwelling
- "ROOF": creates triples which are a represenation of the roof details within the epc assessment of the dwelling
- "WALL": creates triples which are a representation of the wall details within the epc assessment of the dwelling
- "WINDOW": creates triples which are a representation of the window details within the epc assessment of the dwelling
- "HEATING": creates triples which are destined for the heating-v1 graph in the IA node

## UPRN lat long pipeline

The uprn lat long pipeline has two parts, the mapper and the adapter.

### Adapter

The adapter can be found under the `generic-adapter` folder. Before you can run this adapter please ensure you have the address profiling csv file downloaded in an accessible location.
The adapter can be run as a docker container. You must build the docker container running the command `make docker-build SOURCE_FILE=<insert-filepath-here>`.
Once the container has been built use the command `make docker-run SASL_USERNAME=<insert-sasl-username> SASL_PASSWORD=<insert-sasl-password> PRODUCER_NAME=lat-long TARGET_TOPIC=lat-long FILE_NAME=<insert-filename-here>` to run the adapter.
The adapter container is set to be removed once it has completed.

### Mapper

The mapper can be found under the `uprn-lat-long-pipeline/mapper` folder. The mapper can be run as a docker container. You must build the docker container using the command `make docker-build`.
Once the container is built use the command `make docker-run SASL_USERNAME=<insert-sasl-username> SASL_PASSWORD=<insert-sasl-password>`.
The mapper container is not set to be automatically removed once it has done processing. Please remove the container manually using the command `docker rm -f <insert-uprn-lat-long-mapper-container-name>`.

## Post processing pipeline

The post processing pipeline has been created to create smaller named graphs from the main data so that the `IRIS-visualization` application can lazy load the required data quickly as compared to querying the main graph with millions of triples.

### Prerequisites

Before you can run the post processing pipeline please complete the steps below.

- Create a back up of the main data from the secure agent graph using the comand `curl -X http://<insert-secure-agent-graph-host-and-port-here/knowledge/get >> <insert-path-and-filename-for-the-backup>`.
- Stop the main secure agent graph.
- Run a standalone instance of the secure agent graph using the command `docker run -d -p 3031:3030 --name iris-pipeline-sag-standalone -v $(pwd)/config/standalone-config.ttl:/fuseki/config/config.ttl:ro -e JAVA_OPTIONS="-XX:MinRAMPercentage=80.0 -XX:MaxRAMPercentage=80.0" -e JWKS_URL="disabled" iris-pipeline/secure-agent-graph --config /fuseki/config/config.ttl --compact`. Please run this command when you are in the `developer_resources` directory.
- Edit the docker compose file found under the `materialised-view-creation/src/create-view` and replace the `<host-ip>` with the internal IP of the container and the `<secure-agent-graph-port>` with the port of the new instance of the secure agent graph.
- Make sure the host and port in the make command are pointing to the standalone secure agent graph.
- Run the command `make upload-ies-building-ontology` when in the `materialised-view-creation/src/create-view`.

### Running the pipeline

The post processing pipeline can be found under the `materialised-view-creation/src/create-view` folder. The post processing pipeline can be run as docker containers to create the individual named graphs.
You must build the docker container using the command `docker build -t iris-pipeline/create-view .`.
Once you have built the container you can run it using the command `docker compose up -d`. This will kick off the docker containers in parallel.

You can edit the `LIMIT` and `OFFSET` parameters of the containers in the docker compose file and set these as you wish. Sensible defaults are in place.

## Creating spatial indexes

Spatial indices are created by the geosparql enabled secure agent graph to optimize the retrieval of geospacial queries. These are created on startup for a geosparql enabled secure agent graph.

- While in the `developer_resources` directory run another instance of the secure agent graph using the command `docker run -d -p 3032:3030 --name iris-pipeline-sag-geo -v $(pwd)/config/config-geosparql.ttl:/fuseki/config/config.ttl:ro -e JAVA_OPTIONS="-XX:MinRAMPercentage=80.0 -XX:MaxRAMPercentage=80.0" -e JWKS_URL="disabled" iris-pipeline/secure-agent-graph --config /fuseki/config/config.ttl`.
- Upload the backup of the main data to the graph using the command `curl -X POST -H 'Content-Type: text/turtle' -T <insert-back-up-file-here> http://localhost:3032/knowledge/data?default`
- Restart the instance of the sag using the command `docker restart iris-pipeline-geo`.

## Logging and monitoring

The logs from the secure agent graph container can be found using the command `docker logs <insert-secure-agent-graph-name>`.
To see the activity in the kafka cluster it is recommended to setup the kafka ui using the command `docker run -d -p 8081:8080 -e DYNAMIC_CONFIG_ENABLED=true --name kafka-ui provectuslabs/kafka-ui:latest`. You will have to add the kafka cluster manually. Please use the internal IP of the container as the host address.
To query the secure agent graph using a GUI it is recommended to setup the YASGUI using the command `docker run -d -p 8082:80 -e DEFAULT_SPARQL_ENDPOINT=<insert-sparql-endpoint-here> --name yasgui erikap/yasgui:latest`. Use the public IP of the container as the host of the default sparql endpoint.

## Observations

The following observations have been noted while running the pipeline in a deployed environment.

- It is better to run both the mapper and adapters of each pipeline together after stopping the secure agent graph container.
- If you find that you are running out of space while the secure agent graph container is consuming the mapped records, you can stop the container and start it which will force it to trigger initial compaction which will reduce the size of the triple store significantly. It is worth noting this process usually takes around 4 to 5 hours to complete regardless of the size.
- It is worth keeping in mind that the compaction process need some storage space in the first place to work. It is good to keep at least 20 GiB of space for this process.
- Please ensure the secure agent graph is running before running the post processing pipeline.
- The post processing step is quite CPU intensive.
