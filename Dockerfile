FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/raw data/processed data/vector_store eval/results

EXPOSE 8501

CMD ["sh", "-c", "python scripts/setup_data.py && streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]