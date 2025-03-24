FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    # Adding dependencies for Pillow and ReportLab
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy project
COPY . .

# We'll run migrations when the container starts to ensure the .env file is used
# Migrations will be part of an entrypoint script

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "django_simulador.wsgi:application"]