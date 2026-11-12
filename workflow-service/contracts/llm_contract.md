# Llm service contract

## Request schema

- `messages`: array, required; role/content strings for each message
- `model`: nonempty string, required
- `options`: object, optional; per-call Ollama generation settings
- `output_schema`: object or null, optional; passed as Ollama format

## Response schema

- `output`: object or string, required; parsed structured JSON if schema supplied, otherwise response content string

## Errors

ValueError for invalid request or invalid output; connection, HTTP, timeout and malformed response errors propagate. No fallback generation.

All service methods take one request dictionary and return one response dictionary. No HTTP API is used.
