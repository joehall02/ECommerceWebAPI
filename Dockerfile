# Backend image
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port
EXPOSE 5050

# Run the application using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "run:app"]
# CMD ["python3", "run.py"]