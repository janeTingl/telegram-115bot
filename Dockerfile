FROM python:3.12-slim

# 1. 关键：工作目录设在根目录 /app
WORKDIR /app

# 2. 复制 backend 下的依赖并安装
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. 复制所有文件 (此时 /app 下会有 backend 文件夹)
COPY . .

# 4. 暴露端口
EXPOSE 12808

# 5. 关键：启动命令指向 "backend.main"
# 告诉 Python："去 backend 文件夹里找 main.py，里面的 app 对象"
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "12808"]

