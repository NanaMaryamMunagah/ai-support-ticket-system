"""HTTP adapters preserving the the support ticket Python service method contracts."""
import os
import requests
from urllib.parse import urlparse

def service_url(env_name, default):
    url = os.getenv(env_name, default).rstrip('/')
    parsed = urlparse(url)
    if parsed.scheme not in ('http','https') or not parsed.netloc:
        raise ValueError('Invalid service URL')
    return url

class _HTTPService:
    def __init__(self, base_url, endpoint, timeout=120):
        self.url = base_url + endpoint
        self.timeout = timeout
    def _post(self, request):
        response = requests.post(self.url, json=request, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        if not isinstance(result,dict):
            raise ValueError('Invalid service JSON response')
        return result

class RoutingHTTPClient(_HTTPService):
    def __init__(self,base_url):super().__init__(base_url,'/route')
    def route_ticket(self,request):return self._post(request)

class RetrievalHTTPClient(_HTTPService):
    def __init__(self,base_url,top_k=5):
        super().__init__(base_url,'/search')
        self.top_k=top_k
    def retrieve_evidence(self,request):return self._post(request)
