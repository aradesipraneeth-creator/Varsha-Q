# VARSHA-Q Production Containerfile (Single-Service Full Stack)
FROM python:3.11-slim

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

# Copy backend source, data, configs, models, and pre-compiled frontend distribution
COPY backend/ ./backend/
COPY data/ ./data/
COPY configs/ ./configs/
COPY models/ ./models/
COPY scripts/ ./scripts/
COPY frontend/dist/ ./frontend/dist/

ENV PYTHONUNBUFFERED=1
ENV VARSHA_MODE=DEMO
ENV DEVICE=cpu
ENV PORT=10000

EXPOSE 10000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
