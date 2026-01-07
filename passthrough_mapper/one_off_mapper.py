import time
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
        idle_timeout_seconds: int
    ):
        self.bootstrap_servers = bootstrap_servers
        self.sasl_username = sasl_username
        self.sasl_password = sasl_password
        self.source_topic = source_topic
        self.target_topic = target_topic
        self.kafka_consumer_config = kafka_consumer_config
        self.kafka_producer_config = kafka_producer_config
        self.mapping_function = mapping_function
        self.idle_timeout_seconds = idle_timeout_seconds

    def _remaining_from_committed(self, source):
        if not hasattr(source, "consumer"):
            return None
        assignments = source.consumer.assignment()
        if not assignments:
            return None

        committed = source.consumer.committed(assignments, timeout=5.0)
        total = 0
        for tp in committed:
            if tp.offset < 0:
                return None
            low, high = source.consumer.get_watermark_offsets(tp)
            total += max(0, high - tp.offset)
        return total


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
                    total_records_sent_to_dlq = 0

                    remaining = source.remaining()
                    if remaining is None:
                        start = time.monotonic()
                        while remaining is None and time.monotonic() - start < 5:
                            if hasattr(source, "consumer"):
                                source.consumer.poll(0.1)
                                for tp in source.consumer.assignment():
                                    low, high = source.consumer.get_watermark_offsets(tp)
                                    pos = source.consumer.position([tp])[0].offset
                                    committed = source.consumer.committed([tp], timeout=5.0)[0].offset
                                    logger.info(
                                        f"{tp.topic}-{tp.partition} pos={pos} committed={committed} low={low} high={high}"
                                    )
                            time.sleep(0.1)
                            remaining = source.remaining()

                    committed_remaining = self._remaining_from_committed(source)
                    if committed_remaining is not None:
                        remaining = committed_remaining
                    
                    logger.info(f"remaining()={remaining}")

                    if remaining == 0:
                        if self.idle_timeout_seconds is None or self.idle_timeout_seconds <=0:
                            logger.info(
                                f"No records remaining in {self.source_topic}; skipping."
                            )
                            return
                        
                        logger.info(
                            f"No records remaining in {self.source_topic}; waiting up to "
                            f"{self.idle_timeout_seconds}s for new data."
                        )
                        start = time.monotonic()
                        while True:
                            time.sleep(1)
                            committed_remaining = self._remaining_from_committed(source)
                            if committed_remaining is None:
                                break
                            if committed_remaining > 0:
                                logger.info(
                                    f"New records detected in {self.source_topic}; starting processing."
                                )
                                break
                            if time.monotonic() - start >= self.idle_timeout_seconds:
                                logger.info(
                                    f"No new records for {self.idle_timeout_seconds}s in "
                                    f"{self.source_topic}; skipping."
                                )
                                return
                            
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

                            if index > 0 and index % 25000 == 0:
                                logger.info(
                                    f"Processed {index} records, {total_records_sent_to_dlq} records sent to DLQ, {source.remaining()} records remaining"
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
                            total_records_sent_to_dlq += 1

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
