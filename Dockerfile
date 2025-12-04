# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source code
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Python backend with Nginx
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 安装必要依赖：Python 库、Nginx、Supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev libssl-dev nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装后端 Python 依赖
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /app/backend/requirements.txt

# 复制后端代码和其他文件
COPY backend/ /app/backend/
COPY app/ /app/app/
COPY configure-secrets.sh verify-docker-image.sh verify-dockerhub-token.sh /app/
COPY zid.yml VERSION /app/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# 拷贝配置文件到系统目录
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 暴露 Nginx 端口
EXPOSE 12808

# 启动 Supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]