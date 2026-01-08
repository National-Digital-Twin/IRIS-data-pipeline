# SPDX-License-Identifier: Apache-2.0
# Originally developed by Telicent Ltd.; subsequently adapted, enhanced, and maintained by the National Digital Twin Programme.

#
# Copyright (C) Telicent Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#  Modifications made by the National Digital Twin Programme (NDTP)
#  © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
#  and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import json
import logging
import time
from typing import List, Tuple

from confluent_kafka import Consumer, KafkaError, Producer
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
BROKER = os.getenv(
    "BOOTSTRAP_SERVERS",
    default=True,
)
SASL_USERNAME = os.getenv(
    "SASL_USERNAME",
    default=None,
)
SASL_PASSWORD = os.getenv(
    "SASL_PASSWORD",
    default=None,
)
KAFKA_SECURITY_PROTOCOL = os.getenv(
    "KAFKA_SECURITY_PROTOCOL",
    default="SASL_PLAINTEXT",
)
KAFKA_SASL_MECHANISM = os.getenv(
    "KAFKA_SASL_MECHANISM",
    default="PLAIN",
)
AUTO_OFFSET_RESET = os.getenv(
    "AUTO_OFFSET_RESET",
    default="earliest",
)
POLL_TIMEOUT_SECONDS = os.getenv(
    "POLL_TIMEOUT_SECONDS",
    default=1.0,
)
IDLE_TIMEOUT_SECONDS = os.getenv(
    "IDLE_TIMEOUT_SECONDS",
    default=10,
)
COMMIT_INTERVAL = os.getenv(
    "COMMIT_INTERVAL",
    default=1000,
)
PROGRESS_LOG_INTERVAL = os.getenv(
    "PROGRESS_LOG_INTERVAL",
    default=25000,
)

_EXIT = object()


topic_mappings_json = os.getenv("TOPIC_MAPPINGS_JSON", default=None)
if topic_mappings_json:
    topic_mappings = json.loads(topic_mappings_json)
else:
    logging.info("Topic mappings not provided through Airflow config, falling back to JSON file inside container.")
    
    TOPIC_MAPPINGS_FILEPATH = os.getenv("TOPIC_MAPPINGS_FILEPATH", default=None)
    with open(TOPIC_MAPPINGS_FILEPATH, "r", encoding="utf-8") as f:
        topic_mappings = json.load(f)


def _merge_headers(headers: List[Tuple[str, bytes | str]] | None, source_topic: str):
    merged = list(headers or [])
    merged.append(("source_topic", source_topic))
    return merged


def _build_consumer_cfg(group_id: str) -> dict:
    return {
        "bootstrap.servers": BROKER,
        "security.protocol": KAFKA_SECURITY_PROTOCOL,
        "sasl.mechanism": KAFKA_SASL_MECHANISM,
        "sasl.username": SASL_USERNAME,
        "sasl.password": SASL_PASSWORD,
        "group.id": group_id,
        "auto.offset.reset": AUTO_OFFSET_RESET,
        "enable.auto.commit": False,
    }


def _build_producer_cfg() -> dict:
    return {
        "bootstrap.servers": BROKER,
        "security.protocol": KAFKA_SECURITY_PROTOCOL,
        "sasl.mechanism": KAFKA_SASL_MECHANISM,
        "sasl.username": SASL_USERNAME,
        "sasl.password": SASL_PASSWORD,
        "allow.auto.create.topics": True
    }

def _should_exit_idle(last_msg_time: float) -> bool:
    return time.monotonic() - last_msg_time >= IDLE_TIMEOUT_SECONDS


def _poll_message(consumer: Consumer, last_msg_time: float):
    msg = consumer.poll(POLL_TIMEOUT_SECONDS)
    if msg is None:
        if _should_exit_idle(last_msg_time):
            return _EXIT, last_msg_time
        return None, last_msg_time

    if msg.error() is not None:
        if msg.error().code() == KafkaError._PARTITION_EOF:
            if _should_exit_idle(last_msg_time):
                return _EXIT, last_msg_time
            return None, last_msg_time
        logger.error("Consumer error: %s", msg.error())
        return None, last_msg_time

    return msg, time.monotonic()


def _delivery_report(err, msg):
    if err is not None:
        logger.error("Delivery failed: %s", err)


def _produce_message(producer: Producer, msg, source_topic: str, target_topic: str) -> None:
    new_key = f"{source_topic}"
    headers = _merge_headers(msg.headers(), source_topic)
    producer.produce(
        target_topic,
        key=new_key,
        value=msg.value(),
        headers=headers,
        on_delivery=_delivery_report,
    )
    producer.poll(0)


def _commit_if_needed(consumer: Consumer, processed: int) -> None:
    if COMMIT_INTERVAL > 0 and processed % COMMIT_INTERVAL == 0:
        consumer.commit(asynchronous=True)


def run_mapping(source_topic: str, group_id: str, target_topic: str) -> None:
    consumer = Consumer(_build_consumer_cfg(group_id))
    producer = Producer(_build_producer_cfg())
    consumer.subscribe([source_topic])

    logger.info(
        "Consuming from %s (group=%s) -> %s",
        source_topic,
        group_id,
        target_topic,
    )

    last_msg_time = time.monotonic()
    processed = 0

    while True:
        result, last_msg_time = _poll_message(consumer, last_msg_time)
        if result is _EXIT:
            logger.info("Idle timeout reached for %s, exiting.", source_topic)
            break
        if result is None:
            continue

        _produce_message(producer, result, source_topic, target_topic)
        processed += 1

        if PROGRESS_LOG_INTERVAL > 0 and processed % PROGRESS_LOG_INTERVAL == 0:
            logger.info("Processed %d records from %s", processed, source_topic)

        _commit_if_needed(consumer, processed)

    producer.flush()
    if processed > 0:
        try:
            consumer.commit(asynchronous=False)
        except KafkaError as err:
            if err.code() != KafkaError._NO_OFFSET:
                raise
    consumer.close()
    logger.info(
        "Finished %s -> %s, processed %d records",
        source_topic,
        target_topic,
        processed,
    )


for mapping in topic_mappings["topic_mappings"]:
    run_mapping(
        mapping["source"],
        mapping["source_topic_group_id"],
        mapping["target"],
    )
