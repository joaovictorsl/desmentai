FROM python:3.13.7-slim-trixie

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.web.main:app", "--host", "0.0.0.0"]
