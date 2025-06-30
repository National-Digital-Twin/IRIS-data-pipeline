FROM python:3.12-slim

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
	&& addgroup --system app && \
	adduser --system --group app

USER app

WORKDIR /app

# Copy application code
COPY create_view.py .

# Copy sparql query files
COPY ./create-geo-view/create-geo-view.sparql data/
COPY ./create-geo-filter-view/create-roof-view.sparql data/
COPY ./create-geo-filter-view/create-walls-view.sparql data/
COPY ./create-geo-filter-view/create-floors-view.sparql data/
COPY ./create-geo-filter-view/create-windows-view.sparql data/
COPY ./get-total-buildings.sparql data/
COPY ./create-ward-view.sparql data/
COPY ./create-stats-view.sparql data/
COPY ./create-epc-view.sparql data/

# Command to run your script
CMD ["python", "create_view.py"]
