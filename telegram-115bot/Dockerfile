FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖（确保Pillow编译依赖）
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY main.py .

# 创建数据目录
RUN mkdir -p /app/data

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 使用非root用户运行（增强安全性）
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# 启动命令
CMD ["python", "main.py"]