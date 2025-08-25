# Use official Python image
FROM python:3.11


# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose the port Render expects
ENV PORT=8080
EXPOSE 8080

# Start the Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
