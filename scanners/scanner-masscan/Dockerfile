FROM python:3.11-slim

# Install masscan and required dependencies
RUN apt-get update && \
    apt-get install -y masscan git build-essential libpcap-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create masscan configuration directory and exclude file
RUN mkdir -p /etc/masscan && \
    echo "# Reserved/Private IP ranges to exclude from scanning" > /etc/masscan/exclude.conf && \
    echo "127.0.0.0/8" >> /etc/masscan/exclude.conf && \
    echo "10.0.0.0/8" >> /etc/masscan/exclude.conf && \
    echo "172.16.0.0/12" >> /etc/masscan/exclude.conf && \
    echo "192.168.0.0/16" >> /etc/masscan/exclude.conf && \
    echo "169.254.0.0/16" >> /etc/masscan/exclude.conf && \
    echo "224.0.0.0/4" >> /etc/masscan/exclude.conf

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
CMD ["python", "-m", "arq", "app.main:WorkerSettings"]
