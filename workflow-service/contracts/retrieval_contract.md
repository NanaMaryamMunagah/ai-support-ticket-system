# Retrieval service contract

## Request schema

- `Body`: string, required; original ticket body

## Response schema

- `retrieved_evidence`: array, required; ordered VectorStore.query records (rank integer, chunk_id string, distance finite number, content string, metadata object)

## Errors

ValueError for invalid input or malformed retrieval results. Missing index/embedding failures propagate. An empty list is allowed only if genuinely returned by a healthy query.

All service methods take one request dictionary and return one response dictionary. No HTTP API is used.
