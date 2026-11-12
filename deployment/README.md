# Docker Deployment

This directory contains the Docker Compose configuration for the AI-powered customer support ticket system.

## Prerequisites

- Docker Desktop installed and running
- Python 3 for running the integration test
- Sufficient disk space for the Ollama model and retrieval embeddings

Run all commands from the project root.

## 1. Prepare the LLM

Download the Qwen model into the persistent Ollama volume:

    sh llm-service/ollama_setup.sh

This starts the Ollama container and downloads the model if needed.

## 2. Start the Application

    docker compose -f deployment/compose.yaml up --build -d

Check the status of all four services:

    docker compose -f deployment/compose.yaml ps

The services are exposed on these local ports:

| Service | Port |
| --- | --- |
| Workflow API | 8000 |
| Routing API | 8001 |
| Retrieval API | 8002 |
| Ollama | 8003 |

The workflow API documentation is available at http://localhost:8000/docs.

## 3. Run the Integration Test

    python -m pip install requests
    python tests/test_deployment.py

The test uses a synthetic customer support ticket.

## 4. Inspect Logs

    docker compose -f deployment/compose.yaml logs --tail=80 workflow router retrieval ollama

## 5. Stop the Application

    docker compose -f deployment/compose.yaml down

Persistent Docker volumes retain the downloaded model and workflow traces.

## Implementation Notes

The retrieval image builds its LanceDB index from the included knowledge-base records and downloads the configured FastEmbed model during image construction.

The Ollama model is stored in a persistent Docker volume. New installations use the default volume name `ai-support-ticket-ollama`. Existing installations can override this through the `OLLAMA_VOLUME_NAME` environment variable.

The workflow communicates with the other services through the Docker Compose network. Its trace records are stored in a persistent volume and should not include raw ticket text, prompts, summaries, or retrieved content.
