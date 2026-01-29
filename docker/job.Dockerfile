# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary directories
COPY src/common /app/src/common
COPY src/job_server /app/src/job_server

# Set PYTHONPATH to the current directory so imports work correctly
ENV PYTHONPATH=/app

# Run the job server when the container launches
CMD ["python", "src/job_server/main.py"]
