FROM python:3.12

# Create a non-root user and group
RUN groupadd -r mapperuser && useradd -r -g mapperuser mapperuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/mapper.py .
COPY src/namespaces.py .
COPY src/utils.py .
COPY src/models ./models
COPY src/mapping_functions/ ./mapping_functions
COPY custom_mappers ./custom_mappers

USER mapperuser

CMD ["python", "./mapper.py"]
