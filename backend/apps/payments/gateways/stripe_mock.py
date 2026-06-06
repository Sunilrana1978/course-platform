import uuid
import random
from django.conf import settings
from .base import PaymentGateway

# In-memory store simulating Stripe's server-side intent storage
_intents: dict = {}


class StripeMockGateway(PaymentGateway):
    """
    Mock Stripe gateway that returns Stripe-shaped responses.
    Set MOCK_FAILURE_RATE env var (0.0–1.0) to control simulated failure rate.
    """

    def create_intent(self, amount: float, currency: str, metadata: dict) -> dict:
        intent_id = f'pi_{uuid.uuid4().hex[:24]}'
        intent = {
            'id': intent_id,
            'amount': int(amount * 100),  # Stripe uses cents
            'currency': currency,
            'status': 'requires_confirmation',
            'metadata': metadata,
        }
        _intents[intent_id] = intent
        return intent

    def confirm_intent(self, intent_id: str, payment_method: dict) -> dict:
        intent = _intents.get(intent_id)
        if not intent:
            return {'id': intent_id, 'status': 'failed', 'error': 'Intent not found'}

        failure_rate = getattr(settings, 'MOCK_FAILURE_RATE', 0.05)
        if random.random() < failure_rate:
            intent['status'] = 'failed'
            intent['error'] = 'Your card was declined.'
        else:
            intent['status'] = 'succeeded'
            intent['error'] = None

        _intents[intent_id] = intent
        return intent

    def get_intent(self, intent_id: str) -> dict:
        intent = _intents.get(intent_id)
        if not intent:
            return {'id': intent_id, 'status': 'failed', 'error': 'Intent not found'}
        return intent
