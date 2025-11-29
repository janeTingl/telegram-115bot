FROM python:3.11-slim
WORKDIR /app
# 安装编译工具 gcc (如果你的依赖需要编译)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/* && apt-get clean
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# 创建 data 目录
RUN mkdir -p /app/data
EXPOSE 12808
# 启动命令已确认为 main.py
CMD ["python", "main.py"]