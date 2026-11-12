# LLM Service — Ollama

This project uses Ollama to serve the Qwen 2.5 1.5B Instruct model locally.

## Model

- Model: qwen2.5:1.5b-instruct-q4_K_M
- Runtime: Ollama
- Deployment: Docker Compose
- Port: 8003 (host), 11434 (container)

## Setup

From the project root, run:

    sh llm-service/ollama_setup.sh

The script starts Ollama through Docker Compose and downloads the model if necessary.

## Verify Installation

    docker compose -f deployment/compose.yaml exec ollama ollama list

## Start the Complete Application

    docker compose -f deployment/compose.yaml up --build -d

## Notes

The model is stored in a persistent Docker volume, so it remains available after containers are restarted.

The workflow service communicates with Ollama through the internal Docker Compose network.
