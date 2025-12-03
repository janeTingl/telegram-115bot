# ====== 构建前端 ======
FROM node:18 AS frontend
WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

# 复制前端源代码
COPY frontend .

# 构建 dist
RUN npm run build


# ====== 后端镜像 ======
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 安装系统组件
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

# 后端依赖
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install -r /app/backend/requirements.txt

# 后端代码
COPY backend /app/backend

# 复制前端构建产物到 Nginx
COPY --from=frontend /app/frontend/dist /var/www/html

# 配置
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 12808
CMD ["/usr/bin/supervisord"]