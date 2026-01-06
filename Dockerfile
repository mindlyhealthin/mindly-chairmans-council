FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir gunicorn flask pydantic requests openai firebase-admin python-dotenv
EXPOSE 8080
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "--chdir", "backend", "main:app"]
