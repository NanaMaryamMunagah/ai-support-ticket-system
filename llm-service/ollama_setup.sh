#!/bin/sh
set -eu

# Run this script from the project root.

COMPOSE_FILE="deployment/compose.yaml"
MODEL="qwen2.5:1.5b-instruct-q4_K_M"

echo "Starting Ollama..."
docker compose -f "$COMPOSE_FILE" up -d ollama

echo "Downloading the Qwen model if needed..."
docker compose -f "$COMPOSE_FILE" exec -T ollama ollama pull "$MODEL"

echo "Checking installed models..."
docker compose -f "$COMPOSE_FILE" exec -T ollama ollama list

echo "Ollama setup complete."
