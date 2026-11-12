"""End-to-end deployment test using a synthetic support ticket."""
import json
import math
import os
from pathlib import Path
from uuid import UUID
import requests

DEPARTMENTS = {
    'Billing and Payments', 'Customer Service', 'General Inquiry',
    'Human Resources', 'IT Support', 'Product Support',
    'Returns and Exchanges', 'Sales and Pre-Sales',
    'Service Outages and Maintenance', 'Technical Support'
}
EXPECTED_KEYS = {
    'ticket_id','workflow_record_id','terminal_status','recommended_department',
    'class_scores','ticket_body','ticket_summary','retrieved_evidence','trace_id','error'
}

def test_synthetic_ticket():
    # Synthetic example ticket for the public repository.
    ticket = {"ticket_id": 10001, "Body": 'My television screen flickers intermittently. I have already checked the HDMI cable and restarted the device, but the problem continues. Could you advise me on repair options and warranty coverage?'}
    response = requests.post(os.getenv('WORKFLOW_URL','http://localhost:8000')+'/tickets/process',json=ticket,timeout=360)
    response.raise_for_status()
    result=response.json()
    assert set(result)==EXPECTED_KEYS, set(result)^EXPECTED_KEYS
    assert result['ticket_id']==10001
    assert result['terminal_status']=='summary_ready_for_review',result['error']
    assert result['ticket_body']==ticket['Body']
    assert result['recommended_department'] in DEPARTMENTS
    scores=result['class_scores']
    assert isinstance(scores,dict) and set(scores)==DEPARTMENTS
    assert all(type(v) in (int,float) and math.isfinite(v) for v in scores.values())
    assert scores[result['recommended_department']]==max(scores.values())
    summary=result['ticket_summary']
    assert isinstance(summary,dict) and set(summary)=={'summary','customer_request','missing_information'}
    assert all(isinstance(summary[k],str) and summary[k].strip() for k in ('summary','customer_request'))
    assert isinstance(summary['missing_information'],list)
    assert all(isinstance(x,str) for x in summary['missing_information'])
    evidence=result['retrieved_evidence']
    assert isinstance(evidence,list) and len(evidence)<=5
    for rank,hit in enumerate(evidence,1):
        assert set(hit)=={'rank','chunk_id','distance','content','metadata'}
        assert hit['rank']==rank and isinstance(hit['chunk_id'],str) and hit['chunk_id']
        assert type(hit['distance']) in (int,float) and math.isfinite(hit['distance'])
        assert isinstance(hit['content'],str) and isinstance(hit['metadata'],dict)
    UUID(result['workflow_record_id']);UUID(result['trace_id'])
    assert result['error'] is None
    output=Path(__file__).with_name('synthetic_ticket_result.json')
    output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('PASS: end-to-end workflow, response contract, and all four services; saved',output)

if __name__=='__main__':test_synthetic_ticket()
