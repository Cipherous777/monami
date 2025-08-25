FROM python:3.11

WORKDIR /app

# Copy requirements without torch
COPY requirements.txt .

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Install PyTorch CPU (compatible version)
RUN pip install --no-cache-dir torch==2.8.0 -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

ENV PORT=8080
EXPOSE 8080

CMD gunicorn --bind 0.0.0.0:$PORT app:app

