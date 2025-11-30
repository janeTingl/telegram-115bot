# 多阶段构建减小镜像体积
FROM --platform=$BUILDPLATFORM python:3.11-slim as builder

WORKDIR /app

# 安装编译依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 运行时阶段
FROM --platform=$BUILDPLATFORM python:3.11-slim

WORKDIR /app

# 只安装运行时依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# 从构建阶段复制已安装的包
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY . .

RUN mkdir -p /app/data

EXPOSE 12808

CMD ["python", "main.py"]