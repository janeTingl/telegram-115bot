FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY backend .
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

EXPOSE 12808
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "12808"]