from fastapi import FastAPI, HTTPException
from routing_service import RoutingService
app = FastAPI(title='AI Support Ticket Routing API')
service = RoutingService()
@app.get('/health')
def health():
    return {'status':'ok'}
@app.post('/route')
def route(request: dict):
    try:
        return service.route_ticket(request)
    except ValueError:
        raise HTTPException(status_code=422,detail='Invalid routing request')
    except Exception:
        raise HTTPException(status_code=503,detail='Routing service failed')
