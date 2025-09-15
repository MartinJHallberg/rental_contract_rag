# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml .
COPY poetry.lock* .

# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/
COPY .env.example .env

# Create necessary directories
RUN mkdir -p src/data/cache src/data/vector_stores src/data/uploads

# Expose port
EXPOSE 8050

# Set environment variables
ENV PYTHONPATH=/app/src
ENV DASH_HOST=0.0.0.0
ENV DASH_PORT=8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8050/ || exit 1

# Run the application
CMD ["python", "src/app.py"]