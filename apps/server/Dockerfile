# Backend Server Dockerfile
# Team: DevOps

FROM python:3.11-slim

WORKDIR /app

# Copy all packages
COPY packages/ ./packages/
COPY apps/server/ ./apps/server/

# Install dependencies from all packages
RUN pip install --no-cache-dir \
    -r packages/core/requirements.txt \
    -r packages/langchain-client/requirements.txt \
    -r packages/langchain-memory/requirements.txt \
    -r packages/langchain-chains/requirements.txt \
    -r packages/api/requirements.txt

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "apps/server/main.py"]
