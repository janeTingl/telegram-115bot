FROM python:3.11-slim

WORKDIR /app

# 安装编译工具和开发库（Pillow 依赖）
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制程序文件
COPY . .

# 创建 data 目录
RUN mkdir -p /app/data

EXPOSE 12808
CMD ["python", "main.py"]