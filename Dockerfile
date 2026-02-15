FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV OUTPUT_DIR=/app/output
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Default: web UI mode. Override with: docker run ... game-builder python main.py
CMD ["python", "app.py"]
