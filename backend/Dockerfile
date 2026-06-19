FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed and clean up immediately to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user for security
RUN useradd -m appuser \
    && chown -R appuser:appuser /app \
    && mkdir -p data uploads \
    && chown -R appuser:appuser data uploads

USER appuser

EXPOSE 8000

# Membatasi ke 1 worker agar sangat ringan di VPS
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
