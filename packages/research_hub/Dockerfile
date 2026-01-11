# Use Playwright's official image with Chromium pre-installed
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV HEADLESS=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run the API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
