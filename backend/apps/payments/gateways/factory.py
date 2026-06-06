from django.conf import settings
from .base import PaymentGateway
from .stripe_mock import StripeMockGateway

_REGISTRY: dict[str, type] = {
    'stripe': StripeMockGateway,
    # 'paypal': PayPalGateway,   # add future providers here
}


def get_gateway(name: str | None = None) -> PaymentGateway:
    provider = name or getattr(settings, 'PAYMENT_GATEWAY', 'stripe')
    cls = _REGISTRY.get(provider)
    if cls is None:
        raise ValueError(f"Unknown payment gateway: '{provider}'. Registered: {list(_REGISTRY)}")
    return cls()
