# Workflow Service — Standalone Container Commands

From the project root:

```sh
docker build -t ticket-workflow workflow-service
docker run --rm -d --name ticket-workflow -p 8000:8000 ticket-workflow
curl -fsS http://localhost:8000/health
docker stop ticket-workflow
```

The workflow requires reachable routing, retrieval, and Ollama services. Use Docker Compose to start the complete application and test ticket processing. The routing and retrieval APIs can also be tested independently using their documented service contracts.
