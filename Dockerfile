# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/uploaded_files /app/vectorstore

# Copy backend source code
COPY backend/ ./backend/
COPY .env .

# Declare persistent volumes (optional but helpful)
VOLUME ["/app/uploaded_files", "/app/vectorstore"]

# Ensure FastAPI code can find modules
ENV PYTHONPATH=/app/backend

# Expose FastAPI port
EXPOSE 8000

# Add a container healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Default command to run FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
