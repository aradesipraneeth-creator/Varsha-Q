# VARSHA-Q Production Containerfile
FROM python:3.11-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source, data, configs, and pre-trained models
COPY backend/ ./backend/
COPY data/ ./data/
COPY configs/ ./configs/
COPY models/ ./models/
COPY scripts/ ./scripts/

ENV PYTHONUNBUFFERED=1
ENV VARSHA_MODE=DEMO

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
