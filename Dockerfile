FROM node:20-alpine AS frontend
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
RUN npm run build

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt && pip install whitenoise
COPY backend ./backend
COPY --from=frontend /app/dist ./static
COPY config.json zid.yml ./
RUN mkdir -p uploads && chmod 777 uploads
EXPOSE 12808
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "12808"]