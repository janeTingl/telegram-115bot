FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ make git curl libffi-dev libssl-dev nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .
# 如果你要在容器里构建前端，可以去掉下面这行
# COPY dist ./dist

RUN npm install && npm run build

RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt
RUN pip install whitenoise

RUN mv dist backend/static 2>/dev/null || mv build backend/static 2>/dev/null || true

EXPOSE 12808

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "12808"]