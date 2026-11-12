from fastapi import FastAPI, HTTPException
from retrieval_service import RetrievalService
app = FastAPI(title='AI Support Ticket Retrieval API')
service = RetrievalService()
@app.get('/health')
def health():
    return {'status':'ok'}
@app.post('/search')
def search(request: dict):
    try:
        return service.retrieve_evidence(request)
    except ValueError:
        raise HTTPException(status_code=422,detail='Invalid retrieval request')
    except Exception:
        raise HTTPException(status_code=503,detail='Retrieval service failed')
