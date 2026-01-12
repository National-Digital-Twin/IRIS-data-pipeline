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
import re

from confluent_kafka import Consumer, KafkaError, Producer
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
SOURCE_BROKER = os.getenv(
    "SOURCE_BOOTSTRAP_SERVERS",
    default=None,
)

if not SOURCE_BROKER:
    raise ValueError("SOURCE_BOOTSTRAP_SERVERS is required.")

SOURCE_SASL_USERNAME = os.getenv(
    "SOURCE_SASL_USERNAME",
    default=None,
)
SOURCE_SASL_PASSWORD = os.getenv(
    "SOURCE_SASL_PASSWORD",
    default=None,
)
SOURCE_KAFKA_SECURITY_PROTOCOL = os.getenv(
    "SOURCE_KAFKA_SECURITY_PROTOCOL",
    default="SASL_PLAINTEXT",
)
SOURCE_KAFKA_SASL_MECHANISM = os.getenv(
    "SOURCE_KAFKA_SASL_MECHANISM",
    default="PLAIN",
)

logger.info(
    "Source broker params: " \
    f"SOURCE_BROKER: {SOURCE_BROKER} "
    f"SOURCE_KAFKA_SECURITY_PROTOCOL: {SOURCE_KAFKA_SECURITY_PROTOCOL} "
    f"SOURCE_KAFKA_SASL_MECHANISM: {SOURCE_KAFKA_SASL_MECHANISM} "
)

TARGET_BROKER = os.getenv(
    "TARGET_BOOTSTRAP_SERVERS",
    default=None,
)

if not TARGET_BROKER:
    logger.info("TARGET_BOOTSTRAP_SERVERS not supplied, target Kafka broker will be set to the source Kafka broker.")

    TARGET_BROKER=SOURCE_BROKER
    TARGET_SASL_USERNAME=SOURCE_SASL_USERNAME
    TARGET_SASL_PASSWORD=SOURCE_SASL_PASSWORD
    TARGET_KAFKA_SECURITY_PROTOCOL=SOURCE_KAFKA_SECURITY_PROTOCOL
    TARGET_KAFKA_SASL_MECHANISM=SOURCE_KAFKA_SASL_MECHANISM
    
else:
    SOURCE_ENV_NAME = os.getenv(
        "SOURCE_ENV_NAME",
        default=None
    )
    TARGET_ENV_NAME = os.getenv(
        "TARGET_ENV_NAME",
        default=None
    )
    TARGET_SASL_USERNAME = os.getenv(
        "TARGET_SASL_USERNAME",
        default=None,
    )
    TARGET_SASL_PASSWORD = os.getenv(
        "TARGET_SASL_PASSWORD",
        default=None,
    )
    TARGET_KAFKA_SECURITY_PROTOCOL = os.getenv(
        "TARGET_KAFKA_SECURITY_PROTOCOL",
        default="SASL_PLAINTEXT",
    )
    TARGET_KAFKA_SASL_MECHANISM = os.getenv(
        "TARGET_KAFKA_SASL_MECHANISM",
        default="PLAIN",
    )

    logger.info(
        "Target broker params: " \
        f"TARGET_BROKER: {TARGET_BROKER} "
        f"TARGET_KAFKA_SECURITY_PROTOCOL: {TARGET_KAFKA_SECURITY_PROTOCOL} "
        f"TARGET_KAFKA_SASL_MECHANISM: {TARGET_KAFKA_SASL_MECHANISM} "
    )

AUTO_OFFSET_RESET = os.getenv(
    "AUTO_OFFSET_RESET",
    default="earliest",
)
POLL_TIMEOUT_SECONDS = float(os.getenv(
    "POLL_TIMEOUT_SECONDS",
    default=1.0,
))
IDLE_TIMEOUT_SECONDS = float(os.getenv(
    "IDLE_TIMEOUT_SECONDS",
    default=10,
))
COMMIT_INTERVAL = int(os.getenv(
    "COMMIT_INTERVAL",
    default=1000,
))
PROGRESS_LOG_INTERVAL = int(os.getenv(
    "PROGRESS_LOG_INTERVAL",
    default=25000,
))
SAFE_RE = re.compile(r"[^0-9A-Za-z]+")

_EXIT = object()


topic_mappings_json = os.getenv("TOPIC_MAPPINGS_JSON", default=None)
if topic_mappings_json:
    topic_mappings = json.loads(topic_mappings_json)
else:
    logging.info("Topic mappings not provided through Airflow config, falling back to JSON file mounted to the container.")
    
    TOPIC_MAPPINGS_FILEPATH = os.getenv("TOPIC_MAPPINGS_FILEPATH", default=None)
    with open(TOPIC_MAPPINGS_FILEPATH, "r", encoding="utf-8") as f:
        topic_mappings = json.load(f)


def _merge_headers(headers: List[Tuple[str, bytes | str]] | None, source_topic: str):
    merged = list(headers or [])
    merged.append(("source_topic", source_topic))
    return merged


def _build_consumer_cfg(group_id: str) -> dict:
    return {
        "bootstrap.servers": SOURCE_BROKER,
        "security.protocol": SOURCE_KAFKA_SECURITY_PROTOCOL,
        "sasl.mechanism": SOURCE_KAFKA_SASL_MECHANISM,
        "sasl.username": SOURCE_SASL_USERNAME,
        "sasl.password": SOURCE_SASL_PASSWORD,
        "group.id": group_id,
        "auto.offset.reset": AUTO_OFFSET_RESET,
        "enable.auto.commit": False,
    }


def _build_producer_cfg() -> dict:
    return {
        "bootstrap.servers": TARGET_BROKER,
        "security.protocol": TARGET_KAFKA_SECURITY_PROTOCOL,
        "sasl.mechanism": TARGET_KAFKA_SASL_MECHANISM,
        "sasl.username": TARGET_SASL_USERNAME,
        "sasl.password": TARGET_SASL_PASSWORD,
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
            producer.flush()

        _commit_if_needed(consumer, processed)

    if processed % PROGRESS_LOG_INTERVAL != 0:
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
    source_topic = mapping["source_topic"]
    target_topic = mapping["target_topic"]

    if SOURCE_BROKER != TARGET_BROKER:
        source_topic_group_id = (
            f"{source_topic}__to__{target_topic}"
            f"__src__{SAFE_RE.sub("_", SOURCE_ENV_NAME)}__tgt__{SAFE_RE.sub("_", TARGET_ENV_NAME)}"
        )
    else:
        source_topic_group_id = (
            f"{source_topic}__to__{target_topic}"
        )
    
        if source_topic == target_topic:
            raise ValueError(f"Refusing to copy {source_topic} to itself on the same cluster.")

    run_mapping(
        source_topic,
        source_topic_group_id,
        target_topic,
    )
