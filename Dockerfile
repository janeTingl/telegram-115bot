FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ make git curl libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /app/backend/requirements.txt && \
    pip install whitenoise

COPY . /app

COPY app/dist /app/app/dist

EXPOSE 12808

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "12808"]
