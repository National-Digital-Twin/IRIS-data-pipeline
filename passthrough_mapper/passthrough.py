from telicent_lib.config import Configurator
from passthrough_mapper.one_off_mapper import OneOffMapper
from passthrough_mapper.passthrough_mapper import make_passthrough
from dotenv import load_dotenv
import json

load_dotenv()
config = Configurator()
BOOTSTRAP_SERVERS = config.get("BOOTSTRAP_SERVERS", required=True)
SASL_USERNAME = config.get("SASL_USERNAME", required=True)
SASL_PASSWORD = config.get("SASL_PASSWORD", required=True)
KAFKA_SECURITY_PROTOCOL = config.get("KAFKA_SECURITY_PROTOCOL", default="SASL_PLAINTEXT")
KAFKA_SASL_MECHANISM = config.get("KAFKA_SASL_MECHANISM", default="PLAIN")
TOPIC_MAPPINGS_FILEPATH = config.get("TOPIC_MAPPINGS_FILEPATH", required=True)
topic_mappings_json = config.get("TOPIC_MAPPINGS_JSON", required=False)
if topic_mappings_json:
    topic_mappings = json.loads(topic_mappings_json)
else:
    with open(TOPIC_MAPPINGS_FILEPATH) as f:
        topic_mappings = json.load(f)

AUTO_OFFSET_RESET = config.get("AUTO_OFFSET_RESET", default="earliest") 
IDLE_TIMEOUT_SECONDS = config.get("IDLE_TIMEOUT_SECONDS", default=0, converter=int, required_type=int)

for topic_mapping in topic_mappings["topic_mappings"]:
    SOURCE_TOPIC = topic_mapping["source"]
    SOURCE_TOPIC_GROUP_ID = topic_mapping["source_topic_group_id"]
    TARGET_TOPIC = topic_mapping["target"]
    
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
        IDLE_TIMEOUT_SECONDS
    )
    mapper.run()
