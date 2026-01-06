FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/pyproject.toml backend/poetry.lock* ./
RUN pip install --no-cache-dir gunicorn flask pydantic requests openai firebase-admin python-dotenv
COPY backend/ .
EXPOSE 8080
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "main:app"]
