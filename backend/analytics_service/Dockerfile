FROM python:3.11-slim

WORKDIR /app

COPY analytics_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8005

CMD ["python", "analytics_service/main.py"]
