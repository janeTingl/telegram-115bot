FROM python:3.12-slim

# 装一大堆东西，保证什么都能装上
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ make git curl libffi-dev libssl-dev nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制全部文件（包括前端所有东西）
COPY . .

# 构建前端
RUN npm install && npm run build

# 安装后端依赖
RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt
RUN pip install whitenoise

# 把前端 dist 挂到后端
RUN mv dist backend/static 2>/dev/null || mv build backend/static 2>/dev/null || true

EXPOSE 12808

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "12808"]