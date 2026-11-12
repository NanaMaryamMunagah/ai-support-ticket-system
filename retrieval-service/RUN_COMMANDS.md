# Retrieval Service — Standalone Container Commands

From the project root:

```sh
docker build -t ticket-retrieval retrieval-service
docker run --rm -d --name ticket-retrieval -p 8002:8000 ticket-retrieval
curl -fsS http://localhost:8002/health
docker stop ticket-retrieval
```

The workflow requires reachable routing, retrieval, and Ollama services. Use Docker Compose to start the complete application and test ticket processing. The routing and retrieval APIs can also be tested independently using their documented service contracts.
