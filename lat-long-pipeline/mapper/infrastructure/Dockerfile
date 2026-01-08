FROM python:3.12

# Create a non-root user and group
RUN groupadd -r mapperuser && useradd -r -g mapperuser mapperuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/mapper.py .
COPY src/mapping_function.py .
COPY custom_mappers ./custom_mappers

USER mapperuser

CMD ["python", "./mapper.py"]
