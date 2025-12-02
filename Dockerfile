# backend/Dockerfile
FROM python:3.12-slim

# 关键修复：安装编译依赖 + rust（p115client 0.13.1 必须）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    git \
    ca-certificates \
    curl \
    gcc \
    pkg-config \
    libgdbm-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 rust（cryptography 轮子需要）
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app/backend

# 依赖先装（最大化缓存）
COPY backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY backend .

RUN mkdir -p /app/uploads && chmod 777 /app/uploads

EXPOSE 12808

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "12808"]
