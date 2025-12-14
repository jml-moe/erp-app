# Multi-stage build untuk Django dengan Tailwind CSS
# Stage 1: Build Tailwind CSS
FROM node:20-alpine AS tailwind-builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install Node dependencies
RUN npm ci

# Copy Tailwind input file
COPY static/input.css ./static/

# Copy template files untuk Tailwind bisa scan classes
COPY templates/ ./templates/
COPY apps/ ./apps/

# Build Tailwind CSS (akan scan semua HTML files)
RUN npx @tailwindcss/cli -i ./static/input.css -o ./static/output.css

# Stage 2: Python Django application
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Copy built Tailwind CSS from previous stage
COPY --from=tailwind-builder /app/static/output.css ./static/output.css

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port (Railway akan set PORT environment variable)
EXPOSE $PORT

# Run migrations and start server with Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --threads 2 --timeout 120"]

