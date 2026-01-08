FROM python:3.11-slim

WORKDIR /app

# Install packages from research_agent
COPY packages/research_agent/requirements.txt ./packages/
RUN pip install --no-cache-dir -r packages/requirements.txt

# Install Flask
RUN pip install --no-cache-dir flask flask-cors gunicorn

# Copy research_agent package
COPY packages/research_agent /app/packages/research_agent

# Copy main app
COPY apps/research-service/main.py .

# Add packages to Python path
ENV PYTHONPATH=/app/packages:/app

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 120 main:app
