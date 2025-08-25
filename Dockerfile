# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Flask and Gunicorn
RUN pip install --no-cache-dir Flask gunicorn

# Copy your main file
COPY app.py .

# Expose the port Fly expects
ENV PORT=8080
EXPOSE 8080

# Run your Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
