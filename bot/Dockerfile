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
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy entrypoint first and make it executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Copy wait_for_db.py and make sure it's executable
COPY wait_for_db.py /app/
RUN chmod +x /app/wait_for_db.py

# Copy rest of the project
COPY . /app/

# Make sure entrypoint is executable again (in case it gets overwritten)
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

# Run bot
CMD ["python", "main.py"] 