FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build -- --base /

FROM python:3.12-slim
WORKDIR /app

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libffi-dev libssl-dev gcc && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_DATA_DIR=/data
ENV PYTHONPATH=/app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
RUN if [ -f backend/main.py ]; then mv backend/main.py . ; fi

COPY zid.yml .
COPY --from=frontend-builder /app/dist ./dist

VOLUME /data
EXPOSE 12808

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "12808"]