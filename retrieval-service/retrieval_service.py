from pathlib import Path
import math
TABLE_NAME = "support_ticket_chunks"

class RetrievalService:
    def __init__(self, database_path=None, top_k=5):
        if type(top_k) is not int or top_k <= 0:
            raise ValueError('top_k must be a positive integer')
        self.top_k = top_k
        self.database_path = Path(database_path) if database_path else Path(__file__).with_name('vector_db')
        if not self.database_path.is_dir():
            raise FileNotFoundError('Persisted vector database missing; build it once using build_store.py')
        from VectorStore import VectorStore
        self.store = VectorStore(self.database_path)
        self.store._database.open_table(TABLE_NAME)  # fail at initialization if index is missing

    def retrieve_evidence(self, request):
        if not isinstance(request, dict) or not isinstance(request.get('Body'), str) or not request['Body'].strip():
            raise ValueError('Retrieval request requires a nonblank Body string')
        records = self.store.query(request['Body'], top_k=self.top_k)
        if not isinstance(records, list) or len(records) > self.top_k:
            raise ValueError('Invalid retrieval response')
        for i, hit in enumerate(records, 1):
            if (not isinstance(hit, dict) or set(hit) != {'rank','chunk_id','distance','content','metadata'}
                or type(hit['rank']) is not int or hit['rank'] != i
                or not isinstance(hit['chunk_id'], str) or not hit['chunk_id']
                or type(hit['distance']) not in (int,float) or not math.isfinite(hit['distance'])
                or not isinstance(hit['content'], str) or not isinstance(hit['metadata'], dict)):
                raise ValueError('Malformed retrieved evidence')
        return {'retrieved_evidence': records}
