# Routing Service — Standalone Container Commands

From the project root:

```sh
docker build -t ticket-router routing-service
docker run --rm -d --name ticket-router -p 8001:8000 ticket-router
curl -fsS http://localhost:8001/health
docker stop ticket-router
```

The workflow requires reachable routing, retrieval, and Ollama services. Use Docker Compose to start the complete application and test ticket processing. The routing and retrieval APIs can also be tested independently using their documented service contracts.
