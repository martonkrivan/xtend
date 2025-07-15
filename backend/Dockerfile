# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv (ultra-fast Python package manager)
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv install --system

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
