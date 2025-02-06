*This repository contains Alpha code and is being released to meet a contractual obligation to the National Digital Twin
Programme*

# NDT Retrofit Data Pipeline

## Project structure

Some files have been excluded to focus on the key components. 

<pre>
.
├── LICENSE
├── Makefile
├── NOTICE
├── README.md
├── address-profiling-coefficient-pipeline
│   ├── initial_load_adapter
│   │   ├── infrastructure
│   │   │   ├── Dockerfile
│   │   │   └── job.yaml
│   │   ├── input_files (contains any local files required by the adapters)
│   │   ├── requirements.txt
│   │   ├── src
│   │   │   └── producer.py
│   │   └── tests
│   ├── mapper
│   │   ├── infrastructure
│   │   │   ├── Dockerfile
│   │   │   └── job.yaml
│   │   ├── requirements.txt
│   │   ├── src
│   │   │   ├── address_profile_to_knowledge_mapper.py
│   │   │   ├── mapping_function.py
│   │   │   └── ndt_classes.py
│   │   └── tests
│   └── single_file_s3_producer
│       ├── infrastructure
│       │   ├── Dockerfile
│       │   └── job.yaml
│       ├── requirements.txt
│       ├── src
│       │   ├── label_mapper.py
│       │   └── s3-producer.py
│       └── tests
├── iow-uprn-lat-log-coefficient-pipeline
│   ├── adapter
│   │   ├── infrastructure
│   │   │   ├── Dockerfile
│   │   │   └── job.yaml
│   │   ├── input_files (contains any local files required by the adapters)
│   │   ├── requirements.txt
│   │   ├── src
│   │   │   └── producer.py
│   │   └── tests
│   └── mapper
│       ├── infrastructure
│       │   ├── Dockerfile
│       │   └── job.yaml
│       ├── requirements.txt
│       ├── src
│       │   ├── mapping_function.py
│       │   └── osopenuprn_to_knowledge_mapper.py
│       └── tests
├── repository-configuration
│   ├── README.md
│   ├── provider.tf
│   ├── repository.tf
│   ├── terraform.tf
│   └── variables.tf
└── retrofit-ontology-adapter
    ├── infrastructure
    │   ├── Dockerfile
    │   └── job.yaml
    ├── requirements.txt
    ├── src
    │   ├── ndt_retrofit_buildings_extensions.ttl
    │   └── retrofit_ontology_producer.py
    └── tests</pre>

Please follow this structure to add any new sub pipelines to this project.

## There are four sets of things to run here:
### Address (EPC) profiling data (includes EPC rating and info about wall, roof, floor and window detail)
Producer: ```/address-profiling-coefficient-pipeline/initial_load_adapter/src/producer.py```

Mapper: ```/address-profiling-coefficient-pipeline/mapper/src/address_profile_to_knowledge_mapper.py```

### OS data (includes lat-long and TOID data)
Producer: ```/iow-uprn-lat-log-coefficient-pipeline/adapter/src/producer.py```

Mapper: ```/iow-uprn-lat-log-coefficient-pipeline/mapper/src/osopenuprn_to_knowledge_mapper.py```

### Ontology extensions and styles
Producer: ```/retrofit-ontology-adapter/src/retrofit_ontology_producer.py```

### S3 Producer for Address (EPC) profiling updates dropped into an S3 bucket
Producer: ```/address-profiling-coefficient-pipeline/single_file_s3_producer/src/s3-producer.py```

## Running a local instance of Kafka

If you want to run a local instance of Kafka run the following commmand in the terminal:

```
make start-kafka-docker
```

To stop the running Kafka instance run the following command in the terminal:

```
make stop-and-remove-kafka-docker
```
The following details will be required to connect to the local Kafka instance:

  - Username: user1
  - Password: root

## Running the jobs on the cluster

To run the data pipeline on any of the deployed environments they must be run as kubernetees jobs.
This can be done by navigating to the directoy for the aspect of the pipeline that needs to be run and subsequently running the following command

```
kubectl apply -f job.yaml
```

For any of the file based jobs the containers will need to be redeployed with the new files because the scripts look for them locally.

## Running local code development tools

See [RUNNING_CODE_DEV_TOOLS.md](./developer_docs/RUNNING_CODE_DEV_TOOLS.md) for more information.

## Contributors
The development of these works has been made possible with thanks to our [contributors](https://github.com/National-Digital-Twin/IRIS-data-pipeline/graphs/contributors).