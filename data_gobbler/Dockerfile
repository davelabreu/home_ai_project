FROM python:3.10-slim

WORKDIR /app

COPY data_gobbler/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data_gobbler/ .

EXPOSE 8050

CMD ["python", "app.py"]
