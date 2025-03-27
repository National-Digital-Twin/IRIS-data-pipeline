# INSTALLATION

**Repository:** `IRIS-Data-Pipeline`  
**Description:** `Details how to install and run the pipeline`  
**SPDX-License-Identifier:** `Apache-2.0 AND OGL-UK-3.0 ` 

## Prerequisites  
Before using this repository, ensure you have the following dependencies installed:  
- **Required Tooling:** Python, Kafka, Zookeeper (latter two can be installed via Docker following steps below)

### 1. Download 
```sh  
git clone https://github.com/IRIS-Data-Pipeline.git  
cd IRIS-Data-Pipeline
```

### 2. Install Dependencies

It is recommended to use `pip` and a Python virtual environment (venv) to manage versions of the dependencies. The repository follows the below structure for the two main pipelines:
<pre>
.
├── pipeline/
│   ├── component/
│   │   ├── infrastructure/
│   │   │   ├── Dockerfile
│   │   │   └── job.yaml
│   │   ├── Makefile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   └── tests/
</pre>

The dependencies for each individual component (adapter, mapper etc.) are stored within the `requirements.txt` file. 

A `docker-compose.yml` is included at the root of the repository which will provide local versions of Kafka and Zookeeper. A `Makefile` is also included for convenience - run `make start-kafka-docker` at the root of the repository to start Kafka and Zookeeper Docker containers. Docker is a pre-requisite for this installation.

### 3. Configuration
Example `.env` configuration files are provided for each component - named as `.env-local`. To run the pipeline locally, make a copy of the `.env-local` file as `.env` and populate the environment variables. If using the above steps to run Kafka, the following details will be required to connect to the local Kafka instance:

  - `BOOTSTRAP_SERVERS`: `localhost:9092`
  - `SASL_USERNAME`: `user1`
  - `SASL_PASSWORD`: `root`

All of the components are configured to automatically create Kafka topics if they don't already exist, so the topics do not need to be created before the code is run.

A set of input data will be needed to run the adapter components. These are produced as outputs from the [IRIS-Data-Cleanser](https://github.com/National-Digital-Twin/IRIS-data-cleanser) pipeline.

## Deployment

To run the data pipeline on any of the deployed environments they must be run as Kubernetes jobs. This can be done by navigating to the directory for the aspect of the pipeline that needs to be run and subsequently running the following command

```
kubectl apply -f job.yaml
```

For any of the file based jobs the containers will need to be redeployed with the new files because the scripts look for them locally.

© Crown Copyright 2025. This work has been developed by the National Digital Twin Programme and is legally attributed to the Department for Business and Trade (UK) as the governing entity.  
Licensed under the Open Government Licence v3.0.  
For full licensing terms, see [OGL_LICENSE.md](OGL_LICENSE.md).