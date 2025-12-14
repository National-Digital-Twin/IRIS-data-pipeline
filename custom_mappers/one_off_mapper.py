from telicent_lib.logging import CoreLoggerAdapter, CoreLoggerFactory
from telicent_lib.records import RecordMapper
from telicent_lib.sinks import KafkaSink
from telicent_lib.sources import KafkaSource


class OneOffMapper:
    def __init__(
        self,
        bootstrap_servers: [str],
        sasl_username: str,
        sasl_password: str,
        source_topic: str,
        target_topic: str,
        kafka_consumer_config: dict,
        kafka_producer_config: dict,
        mapping_function: RecordMapper,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.sasl_username = sasl_username
        self.sasl_password = sasl_password
        self.source_topic = source_topic
        self.target_topic = target_topic
        self.kafka_consumer_config = kafka_consumer_config
        self.kafka_producer_config = kafka_producer_config
        self.mapping_function = mapping_function

    def run(self):
        logger = self.__create_logger()

        logger.info(f"Processing records in {self.source_topic}...")

        with KafkaSource(
            topic=self.source_topic, kafka_config=self.kafka_consumer_config
        ) as source:
            with KafkaSink(
                topic=self.target_topic, kafka_config=self.kafka_producer_config
            ) as target:
                with KafkaSink(
                    topic=f"{self.target_topic}-dlq",
                    kafka_config=self.kafka_producer_config,
                ) as target_dlq:
                    total_records_to_map = source.remaining()
                    total_records_processed = 0
                    for index, record in enumerate(source.data()):
                        try:
                            if total_records_to_map is None:
                                total_records_to_map = source.remaining()

                            total_records_processed += 1
                            mapped_data = self.mapping_function(record)

                            if mapped_data:
                                target.send(mapped_data)
                            else:
                                logger.info(
                                    f"None returned by mapping function for offset {index}"
                                )

                            if index > 0 and index % 500 == 0:
                                logger.info(
                                    f"Processed {index} records, {source.remaining()} records remaining"
                                )

                            if (
                                total_records_processed >= total_records_to_map
                                and source.remaining() == 0
                            ):
                                logger.info(
                                    f"Finished processing all records in {self.source_topic}!"
                                )
                                break

                        except Exception as err:
                            logger.error(f"Error occured at offset {index}: {err}")

                            target_dlq.send(record)

                            if (
                                total_records_processed >= total_records_to_map
                                and source.remaining() == 0
                            ):
                                logger.info(
                                    f"Finished processing all records in {self.source_topic}!"
                                )
                                break

    def __create_logger(self) -> CoreLoggerAdapter:
        return CoreLoggerFactory.get_logger(
            f"{self.target_topic}-logger",
            kafka_config=self.kafka_producer_config,
            topic=f"{self.target_topic}-logging",
        )
