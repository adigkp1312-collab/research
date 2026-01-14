# Use official Playwright Python image
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Browsers are already installed in this image, but we ensure chromium is there
# and just skip downloading if already present
RUN playwright install chromium

# Copy application code
COPY . .

# Ensure data directory exists
RUN mkdir -p data

# Set environment variables for Chromium in containers
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Disable Chromium sandbox (required for containers)
ENV PLAYWRIGHT_CHROMIUM_SANDBOX=false

# Expose port
EXPOSE 8080

# Command to run the application
CMD ["python3", "-m", "streamlit", "run", "src/ui.py", "--server.fileWatcherType", "none"]
