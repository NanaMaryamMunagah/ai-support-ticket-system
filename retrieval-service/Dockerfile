FROM python:3.14-slim
WORKDIR /app
ENV HF_HOME=/opt/huggingface
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY VectorStore.py preload_embedding.py ./
RUN python preload_embedding.py
COPY retrieval_service.py retrieval_api.py build_store.py prepared_records.json ./
# Persist the knowledge-base LanceDB index into the image during the build, not at request time.
RUN python build_store.py
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=5)" || exit 1
CMD ["uvicorn", "retrieval_api:app", "--host", "0.0.0.0", "--port", "8000"]
