FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./osopenuprn_to_knowledge_mapper.py .
COPY ./mapping_function.py .

CMD ["python", "./osopenuprn_to_knowledge_mapper.py"]