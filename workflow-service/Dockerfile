FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY workflow.py workflow_api.py http_clients.py llm_service.py trace_logger.py workflow_prompt.txt ./
RUN mkdir -p /app/traces
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=5)" || exit 1
CMD ["uvicorn", "workflow_api:app", "--host", "0.0.0.0", "--port", "8000"]
