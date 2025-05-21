# Backend image
FROM python:3.12

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership of the application files to the non-root user
RUN chown -R appuser:appuser /app

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to the non-root user
USER appuser

# Expose the port
EXPOSE 5050

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Run the application using Gunicorn
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "run:app"]
# CMD ["python3", "run.py"]