FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY create_view.py .

# Copy sparql query files
COPY ./create-geo-view/create-geo-view.sparql data/
COPY ./create-geo-filter-view/create-roof-view.sparql data/
COPY ./create-geo-filter-view/create-walls-view.sparql data/
COPY ./create-geo-filter-view/create-floors-view.sparql data/
COPY ./create-geo-filter-view/create-windows-view.sparql data/
COPY get-total-buildings.sparql data/

# Command to run your script
CMD ["python", "create_view.py"]
