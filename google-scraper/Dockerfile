FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir pika

COPY . .

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

CMD ["python", "worker.py"]
