FROM python:3.12

# Create a non-root user and group
RUN groupadd -r mapperuser && useradd -r -g mapperuser mapperuser

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../src/address_profile_to_knowledge_mapper.py .
COPY ../src/mapping_function.py .
COPY ../src/ndt_classes.py .

USER mapperuser

CMD ["python", "./address_profile_to_knowledge_mapper.py"]