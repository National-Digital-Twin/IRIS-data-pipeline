FROM confluentinc/cp-kafka-connect:7.6.0

USER root

# Install Python + pip + curl using the package manager available in this image
RUN set -eux; \
      yum -y install python3 python3-pip curl; \
      yum clean all; \
      rm -rf /var/cache/yum;

WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY mm2-runner.sh /app/mm2-runner.sh
COPY mm2-checker.py /app/mm2-checker.py
RUN chmod +x /app/mm2-runner.sh

ENV MM2_PROPERTIES_PATH=/etc/mm2.properties
ENV KAFKA_LOG4J_OPTS="-Dlog4j.configuration=file:/etc/kafka/connect-log4j.properties"

CMD ["/app/mm2-runner.sh"]
