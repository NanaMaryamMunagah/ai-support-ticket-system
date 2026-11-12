"""the support ticket: parallel routing and retrieval→LLM with correlated tracing."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter
from uuid import uuid4
import math
import os

ROOT = Path(__file__).resolve().parent
from http_clients import RoutingHTTPClient, RetrievalHTTPClient, service_url
from llm_service import LLMClient
from trace_logger import TraceLogger

DEPARTMENTS = (
    'Billing and Payments', 'Customer Service', 'General Inquiry',
    'Human Resources', 'IT Support', 'Product Support',
    'Returns and Exchanges', 'Sales and Pre-Sales',
    'Service Outages and Maintenance', 'Technical Support'
)

MODEL = 'qwen2.5:1.5b-instruct-q4_K_M'
OPTIONS = {'temperature': 0, 'seed': 42, 'num_predict': 512}
SUMMARY_SCHEMA = {
    'type': 'object',
    'properties': {
        'summary': {'type': 'string'},
        'customer_request': {'type': 'string'},
        'missing_information': {'type': 'array', 'items': {'type': 'string'}},
    },
    'required': ['summary', 'customer_request', 'missing_information'],
    'additionalProperties': False,
}
CONTEXT_RULE = ('The following is external approved knowledge-base context, NOT the customer statement. '
    'Use it only to clarify relevant support context; do not attribute article facts or policies to the customer. '
    'Keep the original task: summarize the customer ticket, its request and genuinely missing information. '
    'Do not invent a resolution.')

class TicketWorkflow:
    def __init__(self, log_path=None, top_k=5):
        self.routing = RoutingHTTPClient(service_url('ROUTER_URL','http://router:8000'))
        self.retrieval = RetrievalHTTPClient(service_url('RETRIEVAL_URL','http://retrieval:8000'),top_k=top_k)
        self.llm = LLMClient(ollama_url=service_url('OLLAMA_URL','http://ollama:11434')+'/api/chat')
        self.trace_logger = TraceLogger(log_path or Path(os.getenv('TRACE_LOG_PATH','/app/traces/traces.jsonl')))
        self.base_prompt = Path(__file__).with_name('workflow_prompt.txt').read_text(encoding='utf-8').strip()

    def close(self):
        self.trace_logger.close()

    def _call(self, trace_id, component, fn, request):
        started=perf_counter()
        self.trace_logger.record(trace_id, component=component, event='started')
        try:
            response=fn(request)
            details={}
            if component == 'routing' and isinstance(response, dict):
                details['recommended_department'] = response.get('recommended_department')
            if component == 'retrieval' and isinstance(response, dict):
                evidence=response.get('retrieved_evidence')
                if isinstance(evidence, list):
                    details['retrieved_chunk_ids']=[h.get('chunk_id') for h in evidence if isinstance(h,dict)]
            self.trace_logger.record(trace_id, component=component, event='completed',
                elapsed_ms=round((perf_counter()-started)*1000,3), **details)
            return response
        except Exception as exc:
            self.trace_logger.record(trace_id, component=component, event='failed',
                elapsed_ms=round((perf_counter()-started)*1000,3), error_type=type(exc).__name__)
            raise

    @staticmethod
    def _validate_route(response):
        if not isinstance(response,dict) or set(response) != {'recommended_department','class_scores'}:
            raise ValueError('Invalid routing response')
        scores=response['class_scores']; label=response['recommended_department']
        if (not isinstance(scores,dict) or set(scores)!=set(DEPARTMENTS)
            or any(type(v) not in (int,float) or not math.isfinite(v) for v in scores.values())
            or label not in DEPARTMENTS or scores[label]!=max(scores.values())):
            raise ValueError('Invalid routing scores or department')
        return response

    def _validate_evidence(self,response):
        if not isinstance(response,dict) or set(response)!={'retrieved_evidence'}:
            raise ValueError('Invalid retrieval response')
        hits=response['retrieved_evidence']
        if not isinstance(hits,list) or len(hits)>self.retrieval.top_k:
            raise ValueError('Invalid evidence count')
        for index,hit in enumerate(hits,1):
            if (not isinstance(hit,dict) or set(hit)!={'rank','chunk_id','distance','content','metadata'}
                or type(hit['rank']) is not int or hit['rank']!=index
                or not isinstance(hit['chunk_id'],str) or not hit['chunk_id']
                or type(hit['distance']) not in (int,float) or not math.isfinite(hit['distance'])
                or not isinstance(hit['content'],str) or not isinstance(hit['metadata'],dict)):
                raise ValueError('Invalid evidence record')
        return hits

    @staticmethod
    def _validate_summary(response):
        if not isinstance(response,dict) or set(response)!={'output'}:
            raise ValueError('Invalid LLM response')
        output=response['output']
        if (not isinstance(output,dict) or set(output)!=set(SUMMARY_SCHEMA['required'])
            or not isinstance(output['summary'],str) or not output['summary'].strip()
            or not isinstance(output['customer_request'],str) or not output['customer_request'].strip()
            or not isinstance(output['missing_information'],list)
            or any(not isinstance(x,str) for x in output['missing_information'])):
            raise ValueError('Invalid structured ticket summary')
        return output

    def _summarize(self, trace_id, body):
        evidence=self._validate_evidence(self._call(trace_id,'retrieval',self.retrieval.retrieve_evidence,{'Body':body}))
        context='\n\n'.join(
            f'[Retrieved article {i}: {h["metadata"].get("article_id", "unknown")}, {h["metadata"].get("title", "unknown")}]\n{h["content"]}'
            for i,h in enumerate(evidence,1))
        messages=[
            {'role':'system','content':self.base_prompt+'\n\n'+CONTEXT_RULE+'\n'},
            {'role':'user','content':f'CUSTOMER TICKET BODY (unaltered):\n{body}\n\nEXTERNAL RETRIEVED KNOWLEDGE-BASE CONTEXT:\n{context}'},
        ]
        summary=self._validate_summary(self._call(trace_id,'llm',self.llm.call_llm,
            {'model':MODEL,'messages':messages,'options':OPTIONS,'output_schema':SUMMARY_SCHEMA}))
        return evidence,summary

    def process_ticket(self, request):
        workflow_record_id=str(uuid4())
        trace_id=self.trace_logger.generate_trace_id()
        started=perf_counter()
        self.trace_logger.record(trace_id,component='workflow',event='started',workflow_record_id=workflow_record_id)
        ticket_id=request.get('ticket_id') if isinstance(request,dict) else None
        if type(ticket_id) is not int or ticket_id<=0: ticket_id=None
        result={'ticket_id':ticket_id,'workflow_record_id':workflow_record_id,
                'terminal_status':'workflow_failed','recommended_department':None,
                'class_scores':None,'ticket_body':None,'ticket_summary':None,
                'retrieved_evidence':[],'trace_id':trace_id,'error':None}
        try:
            if ticket_id is None or not isinstance(request.get('Body'),str) or not request['Body'].strip():
                result['terminal_status']='input_rejected'
                result['error']='Invalid ticket_id or Body'
            else:
                body=request['Body']
                with ThreadPoolExecutor(max_workers=2) as executor:
                    route_future=executor.submit(self._call,trace_id,'routing',self.routing.route_ticket,{'Body':body})
                    summary_future=executor.submit(self._summarize,trace_id,body)
                    # Both paths are submitted before either result is awaited.
                    route_result=None; summary_result=None; first_error=None
                    for future,kind in ((route_future,'routing'),(summary_future,'summary')):
                        try:
                            value=future.result()
                            if kind=='routing': route_result=self._validate_route(value)
                            else: summary_result=value
                        except Exception as exc:
                            if first_error is None: first_error=exc
                    if first_error is not None: raise first_error
                evidence,summary=summary_result
                result.update(terminal_status='summary_ready_for_review',
                    recommended_department=route_result['recommended_department'],
                    class_scores=route_result['class_scores'],ticket_body=body,
                    ticket_summary=summary,retrieved_evidence=evidence)
        except Exception as exc:
            # Never put exception messages in traces or responses: third-party exceptions may contain sensitive text.
            result['terminal_status']='workflow_failed'
            result['error']=f'Workflow operation failed ({type(exc).__name__})'
        finally:
            self.trace_logger.record(trace_id,component='workflow',event='completed',
                terminal_status=result['terminal_status'],elapsed_ms=round((perf_counter()-started)*1000,3))
        return result
