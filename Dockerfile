FROM python:3.11

WORKDIR /app

# Copy requirements without torch
COPY requirements.txt .

# Install PyTorch CPU separately
RUN pip install --no-cache-dir torch==2.8.0 -f https://download.pytorch.org/whl/cpu/torch_stable.html


# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
