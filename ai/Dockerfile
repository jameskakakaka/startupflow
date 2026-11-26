FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HF_HOME=/models

COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY startupflow_ai ./startupflow_ai
COPY data ./data
RUN pip install --no-cache-dir --no-deps .

# Models are downloaded on first start into the /models volume (not baked into the image).
VOLUME ["/models"]
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "startupflow_ai.api:app", "--host", "0.0.0.0", "--port", "8000"]
