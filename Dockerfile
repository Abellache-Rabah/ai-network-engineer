FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for some python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    iputils-ping \
    telnet \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Concatenated list from all servers
RUN pip install --no-cache-dir \
    "mcp[cli]" \
    pyyaml \
    nornir \
    nornir_scrapli \
    nornir_utils \
    nornir_napalm \
    napalm \
    pybatfish \
    pydantic

# Copy the entire project
COPY . /app/

# Keep the container alive so we can exec into it
CMD ["tail", "-f", "/dev/null"]
