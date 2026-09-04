FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501

# I dati (parquet) vanno montati come volume:
#   docker run -v /path/to/out/data:/app/data ...
# oppure eseguire la pipeline localmente prima del build.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
