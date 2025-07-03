FROM golang:1.21-alpine AS builder

# Install necessary packages
RUN apk add --no-cache git

# Install nuclei
RUN go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

# Final stage
FROM python:3.11-slim

# Install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy nuclei from builder stage
COPY --from=builder /go/bin/nuclei /usr/local/bin/

# Set up working directory
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for nuclei templates
RUN mkdir -p /root/.config/nuclei/templates

# Download nuclei templates
RUN nuclei -update-templates

COPY app/ app/
CMD ["python", "-m", "arq", "app.main:WorkerSettings"]
