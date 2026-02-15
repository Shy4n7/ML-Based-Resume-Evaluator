FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies (including spacy model)
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application
COPY . .

# Initialize the database
RUN python database.py

# Create the uploads directory for temporary files
RUN mkdir -p uploads && chmod 777 uploads

# Expose port (HF Spaces uses port 7860)
EXPOSE 7860

# Run the application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
