FROM python:3.12-slim

WORKDIR /app

# Force unbuffered Python output for Railway logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will override PORT env var)
EXPOSE 4000

# Run the application with unbuffered flag (redundant but safe)
CMD ["python", "-u", "app.py"]

