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
from telicent_lib.config import Configurator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
config = Configurator()
BROKER = config.get(
    "BOOTSTRAP_SERVERS",
    required=True,
    description="Specifies the Kafka Bootstrap Servers to connect to.",
)
SASL_USERNAME = config.get(
    "SASL_USERNAME",
    required=True,
    description="The username for the SASL authentication.",
)
SASL_PASSWORD = config.get(
    "SASL_PASSWORD",
    required=True,
    description="The password for the SASL authentication.",
)
KAFKA_SECURITY_PROTOCOL = config.get(
    "KAFKA_SECURITY_PROTOCOL",
    required=False,
    default="SASL_PLAINTEXT",
)
KAFKA_SASL_MECHANISM = config.get(
    "KAFKA_SASL_MECHANISM",
    required=False,
    default="PLAIN",
)
AUTO_OFFSET_RESET = config.get(
    "AUTO_OFFSET_RESET",
    default="earliest",
    description="Specifies the starting position for reads.",
)
POLL_TIMEOUT_SECONDS = config.get(
    "POLL_TIMEOUT_SECONDS",
    required=False,
    default=1.0,
    converter=float,
    required_type=float,
)
IDLE_TIMEOUT_SECONDS = config.get(
    "IDLE_TIMEOUT_SECONDS",
    required=False,
    default=10,
    converter=int,
    required_type=int,
)
COMMIT_INTERVAL = config.get(
    "COMMIT_INTERVAL",
    required=False,
    default=1000,
    converter=int,
    required_type=int,
)


topic_mappings_json = config.get("TOPIC_MAPPINGS_JSON", required=False)
if topic_mappings_json:
    topic_mappings = json.loads(topic_mappings_json)
else:
    TOPIC_MAPPINGS_FILEPATH = config.get("TOPIC_MAPPINGS_FILEPATH", required=True)
    with open(TOPIC_MAPPINGS_FILEPATH, "r", encoding="utf-8") as f:
        topic_mappings = json.load(f)


def _normalize_key(source_topic: str, key: bytes | str | None) -> str:
    if key is None:
        base = ""
    elif isinstance(key, bytes):
        base = key.decode("utf-8", "replace")
    else:
        base = str(key)
    return f"{source_topic}|{base}"


def _merge_headers(headers: List[Tuple[str, bytes | str]] | None, source_topic: str):
    merged = list(headers or [])
    merged.append(("source_topic", source_topic))
    return merged


def run_mapping(source_topic: str, group_id: str, target_topic: str) -> None:
    consumer_cfg = {
        "bootstrap.servers": BROKER,
        "security.protocol": KAFKA_SECURITY_PROTOCOL,
        "sasl.mechanism": KAFKA_SASL_MECHANISM,
        "sasl.username": SASL_USERNAME,
        "sasl.password": SASL_PASSWORD,
        "group.id": group_id,
        "auto.offset.reset": AUTO_OFFSET_RESET,
        "enable.auto.commit": False,
    }
    producer_cfg = {
        "bootstrap.servers": BROKER,
        "security.protocol": KAFKA_SECURITY_PROTOCOL,
        "sasl.mechanism": KAFKA_SASL_MECHANISM,
        "sasl.username": SASL_USERNAME,
        "sasl.password": SASL_PASSWORD,
    }

    consumer = Consumer(consumer_cfg)
    producer = Producer(producer_cfg)
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
        msg = consumer.poll(POLL_TIMEOUT_SECONDS)
        if msg is None:
            if time.monotonic() - last_msg_time >= IDLE_TIMEOUT_SECONDS:
                logger.info("Idle timeout reached for %s, exiting.", source_topic)
                break
            continue

        if msg.error() is not None:
            if msg.error().code() == KafkaError._PARTITION_EOF:
                if time.monotonic() - last_msg_time >= IDLE_TIMEOUT_SECONDS:
                    logger.info("Reached end of %s, exiting.", source_topic)
                    break
                continue
            logger.error("Consumer error on %s: %s", source_topic, msg.error())
            continue

        last_msg_time = time.monotonic()
        new_key = _normalize_key(source_topic, msg.key())
        headers = _merge_headers(msg.headers(), source_topic)
        producer.produce(
            target_topic,
            key=new_key,
            value=msg.value(),
            headers=headers,
        )
        producer.poll(0)
        processed += 1

        if COMMIT_INTERVAL > 0 and processed % COMMIT_INTERVAL == 0:
            consumer.commit(asynchronous=True)

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
