from abc import ABC, abstractmethod
from typing import Any


class PaymentGateway(ABC):
    """
    All payment providers must implement this interface.
    Swap providers by returning a different subclass from the factory.
    """

    @abstractmethod
    def create_intent(self, amount: float, currency: str, metadata: dict) -> dict:
        """
        Reserve funds / create a payment intent.
        Returns a dict with at minimum: { 'id': <gateway_ref>, 'status': 'requires_confirmation' }
        """
        ...

    @abstractmethod
    def confirm_intent(self, intent_id: str, payment_method: dict) -> dict:
        """
        Charge the customer using the collected payment method.
        Returns: { 'id': ..., 'status': 'succeeded' | 'failed', 'error': <msg or None> }
        """
        ...

    @abstractmethod
    def get_intent(self, intent_id: str) -> dict:
        """
        Fetch current state of a payment intent (useful for polling after timeout).
        Returns same shape as confirm_intent.
        """
        ...
