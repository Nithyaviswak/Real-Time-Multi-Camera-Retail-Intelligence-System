FROM python:3.11-slim

WORKDIR /app

COPY alert_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8006

CMD ["python", "alert_service/main.py"]
