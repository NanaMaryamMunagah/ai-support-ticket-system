from fastapi import FastAPI, Request
from workflow import TicketWorkflow
app = FastAPI(title='AI Support Ticket Workflow')
workflow = TicketWorkflow()
@app.get('/health')
def health():
    return {'status':'ok'}
@app.post('/tickets/process')
async def process_ticket(request: Request):
    # Invalid JSON is treated as an invalid workflow input, not a 422 FastAPI response.
    try:
        payload = await request.json()
    except ValueError:
        payload = None
    from starlette.concurrency import run_in_threadpool
    return await run_in_threadpool(workflow.process_ticket,payload)
@app.on_event('shutdown')
def shutdown():
    workflow.close()
