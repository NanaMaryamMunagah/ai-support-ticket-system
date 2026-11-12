# Routing service contract

## Request schema

- `Body`: string, required; original ticket body

## Response schema

- `recommended_department`: string, required; one of 10 allowed labels
- `class_scores`: object, required; 10 department keys with finite numeric scores

## Errors

ValueError for invalid input or model response. Model load/inference exceptions propagate. No fallback classification.

All service methods take one request dictionary and return one response dictionary. No HTTP API is used.
