FROM python:3.11-slim

WORKDIR /app

COPY tracking_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8004

CMD ["python", "tracking_service/main.py"]
