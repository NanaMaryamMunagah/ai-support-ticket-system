"""Run once to create the persistent knowledge-base index; never run on every request."""
import json
from pathlib import Path
from VectorStore import VectorStore
root=Path(__file__).resolve().parent
records=json.loads((root/'prepared_records.json').read_text(encoding='utf-8'))
VectorStore(root/'vector_db').build(records)
print(f'Persisted {len(records)} knowledge-base chunks')
