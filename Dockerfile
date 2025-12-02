FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libffi-dev libssl-dev git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端与前端（若前端在 repo 中）
COPY . .

EXPOSE 12808

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "12808"]
