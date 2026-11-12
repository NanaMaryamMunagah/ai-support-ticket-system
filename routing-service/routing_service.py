from pathlib import Path
import math
from ml_candidate import MLCandidate

DEPARTMENTS = (
    'Billing and Payments', 'Customer Service', 'General Inquiry',
    'Human Resources', 'IT Support', 'Product Support',
    'Returns and Exchanges', 'Sales and Pre-Sales',
    'Service Outages and Maintenance', 'Technical Support'
)

class RoutingService:
    def __init__(self, model_path=None):
        path = Path(model_path) if model_path else Path(__file__).with_name('candidate_model.pkl')
        self.classifier = MLCandidate.load(path)

    def route_ticket(self, request):
        if not isinstance(request, dict) or not isinstance(request.get('Body'), str) or not request['Body'].strip():
            raise ValueError('Routing request requires a nonblank Body string')
        result = self.classifier.predict(request['Body'])
        if not isinstance(result, dict) or set(result) != {'recommended_department', 'class_scores'}:
            raise ValueError('Invalid classifier response structure')
        scores = result['class_scores']
        if not isinstance(scores, dict) or set(scores) != set(DEPARTMENTS) or any(
            type(v) not in (float, int) or not math.isfinite(v) for v in scores.values()
        ):
            raise ValueError('Invalid classifier class scores')
        label = result['recommended_department']
        if label not in DEPARTMENTS or scores[label] != max(scores.values()):
            raise ValueError('Classifier label is inconsistent with scores')
        return result
