
FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . .
RUN mkdir -p /app/files_from_modeling_step



CMD ["python", "api.py"]