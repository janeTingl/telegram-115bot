FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
# 修复前端路径，使用绝对路径
RUN npm run build -- --base /

FROM python:3.12-slim
WORKDIR /app
# 安装编译依赖，确保 cryptography 成功安装
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libffi-dev libssl-dev gcc && rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_DATA_DIR=/data
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
# 将 main.py 移动到 /app 根目录以匹配 CMD 启动命令
RUN if [ -f backend/main.py ]; then mv backend/main.py . ; fi
COPY zid.yml .
COPY --from=frontend-builder /app/dist ./dist
VOLUME /data
EXPOSE 12808
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "12808"]
