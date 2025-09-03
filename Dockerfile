# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml .
COPY dead-simpl-landing-firebase-adminsdk-fbsvc-a58f8edb4a.json .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Set environment variables for Firebase
ENV FIREBASE_SERVICE_ACCOUNT_KEY=/app/dead-simpl-landing-firebase-adminsdk-fbsvc-a58f8edb4a.json
ENV FIREBASE_PROJECT_ID=dead-simpl-landing

# Client-side Firebase configuration
ENV FIREBASE_API_KEY=AIzaSyBD3eDWNqTTShUVwMrKh0mVG1-JFnhICkM
ENV FIREBASE_AUTH_DOMAIN=dead-simpl-landing.firebaseapp.com
ENV FIREBASE_STORAGE_BUCKET=dead-simpl-landing.firebasestorage.app
ENV FIREBASE_MESSAGING_SENDER_ID=643606161991
ENV FIREBASE_APP_ID=1:643606161991:web:c9305e31acf9d2fe7b9f62
ENV FIREBASE_MEASUREMENT_ID=G-YQXCM61EM3

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
