# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Update CA certificates and configure pip
RUN update-ca-certificates
ENV PIP_TRUSTED_HOST=pypi.org,pypi.python.org,files.pythonhosted.org

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data data/space data/quiz data/guilds

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the bot
CMD ["python", "bot.1.0.py"]