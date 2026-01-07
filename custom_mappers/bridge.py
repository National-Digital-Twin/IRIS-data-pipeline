from telicent_lib.config import Configurator
from custom_mappers.one_off_mapper import OneOffMapper
from custom_mappers.bridge_mapping import make_passthrough
from dotenv import load_dotenv

load_dotenv()
config = Configurator()
BOOTSTRAP_SERVERS = config.get("BOOTSTRAP_SERVERS", required=True)
SASL_USERNAME = config.get("SASL_USERNAME", required=True)
SASL_PASSWORD = config.get("SASL_PASSWORD", required=True)
KAFKA_SECURITY_PROTOCOL = config.get("KAFKA_SECURITY_PROTOCOL", default="SASL_PLAINTEXT")
KAFKA_SASL_MECHANISM = config.get("KAFKA_SASL_MECHANISM", default="PLAIN")
SOURCE_TOPIC = config.get("SOURCE_TOPIC", required=True)
SOURCE_TOPIC_GROUP_ID = config.get("SOURCE_TOPIC_GROUP_ID", required=True)
TARGET_TOPIC = config.get("TARGET_TOPIC", required=True)
AUTO_OFFSET_RESET = config.get("AUTO_OFFSET_RESET", default="earliest") 

consumer_cfg = {
    "bootstrap.servers": BOOTSTRAP_SERVERS,
    "security.protocol": KAFKA_SECURITY_PROTOCOL,
    "sasl.mechanism": KAFKA_SASL_MECHANISM,
    "sasl.username": SASL_USERNAME,
    "sasl.password": SASL_PASSWORD,
    "group.id": SOURCE_TOPIC_GROUP_ID,
    "auto.offset.reset": AUTO_OFFSET_RESET,
}

producer_cfg = {
    "bootstrap.servers": BOOTSTRAP_SERVERS,
    "security.protocol": KAFKA_SECURITY_PROTOCOL,
    "sasl.mechanism": KAFKA_SASL_MECHANISM,
    "sasl.username": SASL_USERNAME,
    "sasl.password": SASL_PASSWORD,
    "allow.auto.create.topics": True,
}

mapper = OneOffMapper(
    BOOTSTRAP_SERVERS,
    SASL_USERNAME,
    SASL_PASSWORD,
    SOURCE_TOPIC,
    TARGET_TOPIC,
    consumer_cfg,
    producer_cfg,
    make_passthrough(SOURCE_TOPIC),
)
mapper.run()
