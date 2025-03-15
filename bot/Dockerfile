FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    dos2unix && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies first
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY bot/entrypoint.sh /app/entrypoint.sh
# Fix line endings and make executable
RUN dos2unix /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Copy wait_for_db script
COPY bot/wait_for_db.py /app/wait_for_db.py
# Fix line endings and make executable
RUN dos2unix /app/wait_for_db.py && \
    chmod +x /app/wait_for_db.py  

# Copy the rest of the application
COPY bot/ /app/

# Make entrypoint executable again (in case it was overwritten)
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

# Run bot
CMD ["python", "main.py"] 