# 前端构建阶段
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# 后端阶段
FROM python:3.12-slim AS backend
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ make git curl libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装后端依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制后端代码
COPY backend/ ./backend

# 复制前端构建产物
COPY --from=frontend-build /app/frontend/dist ./dist

EXPOSE 12808
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "12808"]
