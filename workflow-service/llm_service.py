import json
from urllib.request import Request, urlopen

class LLMClient:
    def __init__(self, ollama_url='http://localhost:11434/api/chat', timeout=240):
        if not isinstance(ollama_url, str) or not ollama_url.startswith(('http://','https://')):
            raise ValueError('Invalid Ollama URL')
        self.ollama_url = ollama_url
        self.timeout = timeout

    def call_llm(self, request):
        if not isinstance(request, dict) or not isinstance(request.get('model'), str) or not request['model'].strip():
            raise ValueError('LLM request requires model')
        messages = request.get('messages')
        if not isinstance(messages, list) or not messages or any(
            not isinstance(m, dict) or m.get('role') not in ('system','user','assistant')
            or not isinstance(m.get('content'), str) for m in messages
        ):
            raise ValueError('LLM request requires valid messages')
        options = request.get('options', {})
        schema = request.get('output_schema')
        if not isinstance(options, dict) or (schema is not None and not isinstance(schema, dict)):
            raise ValueError('Invalid LLM generation options or output schema')
        payload = {'model':request['model'], 'messages':messages, 'stream':False, 'options':options}
        if schema is not None: payload['format'] = schema
        req=Request(self.ollama_url, data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type':'application/json'},method='POST')
        with urlopen(req, timeout=self.timeout) as response:
            raw=json.load(response)
        content=raw['message']['content']
        if not isinstance(content, str):
            raise ValueError('LLM returned non-string content')
        return {'output': json.loads(content) if schema is not None else content}
