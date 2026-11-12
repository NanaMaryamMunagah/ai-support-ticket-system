# End-to-End Integration Test

This directory contains an integration test for the AI-powered customer support ticket system.

## Running the Test

Start the application from the project root:

    docker compose -f deployment/compose.yaml up --build -d

Wait until all four services are healthy:

    docker compose -f deployment/compose.yaml ps

Then install the test dependency and run:

    python -m pip install requests
    python tests/test_deployment.py

## What the Test Validates

The test uses a synthetic customer support ticket and checks:

- The workflow response contains the expected fields.
- The predicted department is valid.
- Classification scores are present and consistent.
- Retrieved knowledge-base evidence has the expected structure.
- The generated summary follows the expected format.
- Workflow and trace identifiers are valid.
- Processing completes without workflow errors.

## Test Output

The test saves its response to `synthetic_ticket_result.json`.

This generated file is excluded from Git through `.gitignore`.

The test requires the complete application to be running.
