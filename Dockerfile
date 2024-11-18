# Backend image
FROM python:3.10.5-slim-buster

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python3", "run.py"]