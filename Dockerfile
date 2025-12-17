FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will override PORT env var)
EXPOSE 4000

# Run the full trading bot with paper trading support
# This enables the full bot instance (unlike app.py which is API-only)
CMD ["python", "main.py"]

