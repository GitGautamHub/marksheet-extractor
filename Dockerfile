FROM python:3.10-slim-bullseye
WORKDIR /app
RUN apt-get update && apt-get install -y poppler-utils libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .