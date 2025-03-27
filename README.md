# README

**Repository:** `IRIS-Data-Pipeline`

**Description:** `This repository holds two major data pipelines. Firstly, the address-profiling-pipeline processes EPC assessment data, including data points such as the type and location of insulation within the building as well as the SAP band and rating. Secondly, the lat-long-pipeline processes geographic data, such as the building's longitude and latitude coordinates and TOID. Both pipelines implement an Adapter and Mapper components. The former fetches data from a source (e.g. a CSV, an S3 bucket object) and transforms it for ingestion. The latter can be used to perform mappings (e.g. filtering records you don't want to map, mapping each input record to a single output record, mapping each input record to many output records).`

**SPDX-License-Identifier:** `Apache-2.0 AND OGL-UK-3.0 `  

## Overview

This repository contributes to the development of **secure, scalable, and interoperable data-sharing infrastructure**. It supports NDTP’s mission to enable **trusted, federated, and decentralised** data-sharing across organisations.  

This repository is one of several open-source components that underpin NDTP’s **Integration Architecture (IA)**—a framework designed to allow organisations to manage and exchange data securely while maintaining control over their own information. The IA is actively deployed and tested across multiple sectors, ensuring its adaptability and alignment with real-world needs.

## Prerequisites  
Before using this repository, ensure you have the following dependencies installed:  
- **Required Tooling:** Python v3.12.0 (onwards), Docker, Kafka, Zookeeper (or equivalent)
- **Pipeline Requirements:** N/A
- **Supported Kubernetes Versions:** v1.8 (onwards)
- **System Requirements:** Dual-Core CPU (Intel i5 or AMD Ryzen 3 equivalent), 8GB RAM, SSD/HDD with 10GB free space

## Quick Start  
Follow these steps to get started quickly with this repository. For detailed installation, configuration, and deployment, refer to the relevant MD files.  

### 1. Download and Build  
```sh  
git clone https://github.com/IRIS-data-pipeline.git  
cd IRIS-data-pipeline
```

### 2. Run Build Version
```sh  
python --version
```

### 3. Full Installation  
Refer to [INSTALLATION.md](INSTALLATION.md) for detailed installation steps, including required dependencies and setup configurations.  

### 4. Uninstallation  
For steps to remove this repository and its dependencies, see [UNINSTALL.md](UNINSTALL.md).  

## Features
This repository contains the following significant features:
- **address-profiling-pipeline**: Ingests EPC-related data from either a CSV or a S3 bucket object via its adapter components and converts this to an RDF representation of the data.
- **lat-long-pipeline**: Ingests geographic data from a CSV via its adapter components and converts this to an RDF representation of the data.
- **Kafka integration**: The pipelines both consume data (mapper components) and persist data to Kafka topics (adapter & mapper components). 

## Public Funding Acknowledgment  
This repository has been developed with public funding as part of the National Digital Twin Programme (NDTP), a UK Government initiative. NDTP, alongside its partners, has invested in this work to advance open, secure, and reusable digital twin technologies for any organisation, whether from the public or private sector, irrespective of size.  

## License  
This repository contains both source code and documentation, which are covered by different licenses:  
- **Code:** Originally developed by Telicent, now maintained by National Digital Twin Programme. Licensed under the Apache License 2.0.
- **Documentation:** Licensed under the Open Government Licence v3.0.  

See `LICENSE.md`, `OGL_LICENCE.md`, and `NOTICE.md` for details.  

## Security and Responsible Disclosure  
We take security seriously. If you believe you have found a security vulnerability in this repository, please follow our responsible disclosure process outlined in `SECURITY.md`.  

## Contributing  
We welcome contributions that align with the Programme’s objectives. Please read our `CONTRIBUTING.md` guidelines before submitting pull requests.

## Acknowledgements  
This repository has benefited from collaboration with various organisations. For a list of acknowledgments, see `ACKNOWLEDGEMENTS.md`.  

## Support and Contact  
For questions or support, check our Issues or contact the NDTP team on ndtp@businessandtrade.gov.uk.

**Maintained by the National Digital Twin Programme (NDTP).**  

© Crown Copyright 2025. This work has been developed by the National Digital Twin Programme and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
