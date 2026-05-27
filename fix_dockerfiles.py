import os

services = ["alert_service", "analytics_service", "api_gateway", "detection_service", "stream_manager", "tracking_service"]

for svc in services:
    df_path = f"backend/{svc}/Dockerfile"
    if not os.path.exists(df_path):
        continue
        
    with open(df_path, "r") as f:
        content = f.read()
        
    # Fix the COPY requirements
    content = content.replace("COPY requirements.txt .", f"COPY {svc}/requirements.txt .")
    
    # Fix python main.py
    content = content.replace('CMD ["python", "main.py"]', f'CMD ["python", "{svc}/main.py"]')
    
    # Fix uvicorn main:app
    content = content.replace('CMD ["uvicorn", "main:app"', f'CMD ["uvicorn", "{svc}.main:app"')
    
    with open(df_path, "w") as f:
        f.write(content)

print("Dockerfiles updated successfully.")
