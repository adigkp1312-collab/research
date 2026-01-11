FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install core package
COPY packages/core/requirements.txt ./packages/core/
RUN pip install --no-cache-dir -r packages/core/requirements.txt

# Copy and install langchain_client (now vertex_client)
COPY packages/langchain_client/requirements.txt ./packages/langchain_client/
RUN pip install --no-cache-dir -r packages/langchain_client/requirements.txt

# Copy and install langchain_memory
COPY packages/langchain_memory/requirements.txt ./packages/langchain_memory/
RUN pip install --no-cache-dir -r packages/langchain_memory/requirements.txt

# Copy and install langchain_chains
COPY packages/langchain_chains/requirements.txt ./packages/langchain_chains/
RUN pip install --no-cache-dir -r packages/langchain_chains/requirements.txt

# Install API dependencies
COPY apps/server/requirements.txt ./apps/server/
RUN pip install --no-cache-dir -r apps/server/requirements.txt

# Copy all packages
COPY packages/core /app/packages/core
COPY packages/langchain_client /app/packages/langchain_client
COPY packages/langchain_memory /app/packages/langchain_memory
COPY packages/langchain_chains /app/packages/langchain_chains
COPY packages/api /app/packages/api

# Copy server app
COPY apps/server /app/apps/server

# Add packages to Python path
ENV PYTHONPATH=/app

# Cloud Run requires PORT environment variable
ENV PORT=8080

# Expose port
EXPOSE 8080

# Use gunicorn with uvicorn workers for Cloud Run
# The app is imported from packages.api.src.app
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 300 --worker-class uvicorn.workers.UvicornWorker packages.api.src.app:app
