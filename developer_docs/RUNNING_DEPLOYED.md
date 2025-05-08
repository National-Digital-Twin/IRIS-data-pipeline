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

The adapter can be found under the `address-profiling-pipeline/initial-load-adapter` folder. Before you can run this adapter please ensure you have the address profiling csv file downloaded in an accessible location.
The adapter can be run as a docker container. You must build the docker container running the command `make docker-build SOURCE_FILE=<insert-filepath-here>`.
Once the container has been built use the command `make docker-run SASL_USERNAME=<insert-sasl-username> SASL_PASSWORD=<insert-sasl-password> FILE_NAME=<insert-filename-here>` to run the adapter.
The adapter container is set to be removed once it has completed.

### Mapper

The mapper can be found under the `address-profiling-pipeline/mapper` folder. The mapper can be run as a docker container. You must build the docker container using the command `make docker-build`.
Once the container has been built use the command `make docker-run SASL_USERNAME=<insert-sasl-username> SASL_PASSWORD=<insert-sasl-password>`.
The mapper container is not set to be automatically removed once it has done processing. Please remove the container manually using the command `docker rm -f <insert-address-profiling-mapper-container-name>`.

## UPRN lat long pipeline

The uprn lat long pipeline has two parts, the mapper and the adapter.

### Adapter

The adapter can be found under the `uprn-lat-long-pipeline/adapter` folder. Before you can run this adapter please ensure you have the address base plus csv file downloaded in an accessible location.
The adapter can be run as a docker container. You must build the docker container by running the command `make docker-build SOURCE_FILE=<insert-filepath-here>`.
Once the container has been built use the command `make docker-run SASL_USERNAME=<insert-sasl-username> SASL_PASSWORD=<insert-sasl-password> FILE_NAME=<insert-filename-here>` to run the adapter.
The adapter container is set to be removed once it has completed.

### Mapper

The mapper can be found under the `uprn-lat-long-pipeline/mapper` folder. The mapper can be run as a docker container. You must build the docker container using the command `make docker-build`.
Once the container is built use the command `make docker-run SASL_USERNAME=<insert-sasl-username> SASL_PASSWORD=<insert-sasl-password>`.
The mapper container is not set to be automatically removed once it has done processing. Please remove the container manually using the command `docker rm -f <insert-uprn-lat-long-mapper-container-name>`.

## Post processing pipeline

The post processing pipeline has been created to create smaller named graphs from the main data so that the `IRIS-visualization` application can lazy load the required data quickly as compared to querying the main graph with millions of triples.

### Prerequisites

Before you can run the post processing pipeline please complete the steps below.

- Edit the docker compose file found under the `materialised-view-creation/src/create-view` and replace the `<host-ip>` with the internal IP of the container.
- Run the command `make upload-ies-building-ontology` when in the `materialised-view-creation/src/create-view`.

### Running the pipeline

The post processing pipeline can be found under the `materialised-view-creation/src/create-view` folder. The post processing pipeline can be run as docker containers to create the individual named graphs.
You must build the docker container using the command `docker build -t iris-pipeline/create-view .`.
Once you have built the container you can run it using the command `docker compose up -d`. This will kick off the docker containers in parallel.

You can edit the `LIMIT` and `OFFSET` parameters of the containers in the docker compose file and set these as you wish. Sensible defaults are in place.

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
