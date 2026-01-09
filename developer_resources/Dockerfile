ARG IA_NODE_IMAGE_TAG

FROM ${IA_NODE_IMAGE_TAG}
USER root:root

COPY --chown=root:root --chmod=755 ./config/config.ttl /fuseki/config
COPY --chown=root:root --chmod=755 ./config/attribute-store.ttl /fuseki/config
COPY --chown=root:root --chmod=755 ./kafka/consumer.properties /fuseki/kafka/consumer.properties
