# Stage 1: Build Frontend
FROM node:20-alpine as frontend-builder
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Runtime Backend
FROM python:3.12-slim
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .
# 复制前端构建产物
COPY --from=frontend-builder /app/dist ./dist
# 复制分类字典
COPY zid.yml .

# 创建数据目录
VOLUME /data

# 暴露端口: 12808(WebUI/API)
EXPOSE 12808

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "12808"]
