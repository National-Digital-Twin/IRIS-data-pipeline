FROM python:3.12

# Create a non-root user and group
RUN apt-get update && \
	groupadd -r projectoruser && useradd -r -g projectoruser projectoruser

WORKDIR /app

COPY ../custom_projectors ./custom_projectors
COPY ../src/projection_function.py .
COPY ../batched_postgres_projector_template.py projector.py


COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER projectoruser

CMD ["python", "./projector.py"]
