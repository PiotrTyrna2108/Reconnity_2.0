FROM python:3.11-slim

# Install nmap
RUN apt-get update && \
    apt-get install -y nmap && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
CMD ["python", "-m", "arq", "app.main:WorkerSettings"]
