FROM python:3.10-slim

WORKDIR /app

# Install system packages needed for ARM64 builds
# - build-essential / gcc / python3-dev: For faiss-cpu, PyMuPDF
# - pkg-config / libssl-dev: For native extensions like PyMuPDF
# - file: Useful for dev + tooling
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    libssl-dev \
    pkg-config \
    file \
 && rm -rf /var/lib/apt/lists/*


# Upgrade pip tooling and install dependencies (including ruff)
COPY scripts/requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt
