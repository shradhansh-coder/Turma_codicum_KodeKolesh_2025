FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    libtesseract-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only source (avoid __pycache__ etc.)
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5000

# Run Flask app
# Environment defaults (override in compose / runtime)
ENV FLASK_APP=app.py \
    FLASK_DEBUG=0 \
    PYTHONUNBUFFERED=1

# Run as non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["python", "app.py"]
