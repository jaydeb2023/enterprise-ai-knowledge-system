FROM python:3.10-slim

WORKDIR /worker

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/worker ./worker
COPY backend/app ./app

ENV PYTHONPATH=/worker

CMD ["python", "worker/main.py"]
