from telicent_lib.logging import CoreLoggerAdapter, CoreLoggerFactory
from telicent_lib.records import RecordProjector
from telicent_lib.sinks import KafkaSink
from telicent_lib.sources import KafkaSource


class OneOffProjector:
    def __init__(
        self,
        source_topic: str,
        kafka_consumer_config: dict,
        kafka_producer_config: dict,
        projection_function: RecordProjector,
    ):
        self.source_topic = source_topic
        self.kafka_consumer_config = kafka_consumer_config
        self.kafka_producer_config = kafka_producer_config
        self.projection_function = projection_function

    def run(self):
        logger = self.__create_logger()

        logger.info(f"Processing records in {self.source_topic}...")

        with KafkaSource(
            topic=self.source_topic,
            kafka_config=self.kafka_consumer_config,
        ) as source:
            with KafkaSink(
                topic=f"{self.source_topic}-projected-dlq",
                kafka_config=self.kafka_producer_config,
            ) as target_dlq:
                total_records_to_project = source.remaining()
                total_records_processed = 0
                total_records_sent_to_dlq = 0
                for index, record in enumerate(source.data()):
                    try:
                        if total_records_to_project is None:
                            total_records_to_project = source.remaining()

                        total_records_processed += 1
                        self.projection_function(record)

                        if index > 0 and index % 25000 == 0:
                            logger.info(
                                f"Processed {index} records, {total_records_sent_to_dlq} records sent to DLQ, {source.remaining()} records remaining"
                            )

                        if (
                            total_records_processed >= total_records_to_project
                            and source.remaining() == 0
                        ):
                            logger.info(
                                f"Finished processing all records in {self.source_topic}!"
                            )
                            break

                    except Exception as err:
                        logger.error(f"Error occured at offset {index}: {err}")

                        target_dlq.send(record)
                        total_records_sent_to_dlq += 1

                        if (
                            total_records_processed >= total_records_to_project
                            and source.remaining() == 0
                        ):
                            logger.info(
                                f"Finished processing all records in {self.source_topic}!"
                            )
                            break

    def __create_logger(self) -> CoreLoggerAdapter:
        return CoreLoggerFactory.get_logger(
            f"{self.source_topic}-projected-logger",
            kafka_config=self.kafka_producer_config,
            topic=f"{self.source_topic}-to-projected-logging",
        )
