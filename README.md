*This repository contains Alpha code and is being released to meet a contractual obligation to the National Digital Twin
Programme*

# NDT Retrofit Data Pipeline

There are four sets of things to run here:
## Address (EPC) profiling data (includes EPC rating and info about wall, roof, floor and window detail)
Producer: ```/address-profiling-coefficient-pipeline/initial_load_adapter/producer.py```

Mapper: ```/address-profiling-coefficient-pipeline/mapper/address_profile_to_knowledge_mapper.py```

## OS data (includes lat-long and TOID data)
Producer: ```/iow-uprn-lat-log-coefficient-pipeline/adapter/producer.py```

Mapper: ```/iow-uprn-lat-log-coefficient-pipeline/mapper/osopenuprn_to_knowledge_mapper.py```

## Ontology extensions and styles
Producer: ```/retrofit-ontology-adapter/retrofit_ontology_producer.py```

## S3 Producer for Address (EPC) profiling updates dropped into an S3 bucket
Producer: ```/address-profiling-coefficient-pipeline/single_file_s3_producer/s3-producer.py```
