# Production Dockerfile for Capital Market Newsletter
# Python 3.13 + ffmpeg for podcast audio merging

FROM python:3.13-slim

# Install ffmpeg for audio processing (required by TTS service)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for cache (will be mounted as volumes in production)
RUN mkdir -p audio_cache newsletter_cache data

# Default port (Railway overrides via PORT env var)
ENV PORT=5000
EXPOSE 5000

# Run the application with uvicorn (uses $PORT from environment)
CMD uvicorn backend.web_app:app --host 0.0.0.0 --port $PORT
