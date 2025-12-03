FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ make git curl libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先拷贝依赖文件进行安装（为了利用 Docker 缓存层）
COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /app/backend/requirements.txt && \
    pip install whitenoise

# 【核心修正】
# 这一行把当前目录下的所有文件（包括 backend 和 frontend 文件夹）都复制到了 /app
# 所以你的静态文件现在自然就在：/app/frontend/dist
COPY . /app

# 删除掉原来那行 "COPY app/dist ..."，它是多余的，且容易造成路径混乱

EXPOSE 12808

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "12808"]