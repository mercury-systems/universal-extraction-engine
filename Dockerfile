FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libxml2-dev libxslt1-dev zlib1g-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["python3", "src/main.py"]
