FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ make git curl libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

WORKDIR /app

COPY . .

RUN cd /app && npm ci && npm run build

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install whitenoise

RUN mv /app/dist /app/backend/static || true

EXPOSE 12808

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "12808"]
