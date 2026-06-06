from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Payment
from .gateways.factory import get_gateway


class PaymentInProgressError(Exception):
    pass


class PaymentAlreadyCompletedError(Exception):
    def __init__(self, payment):
        self.payment = payment
        super().__init__('Payment already completed.')


def initiate_payment(user, cart_items, idempotency_key: str) -> Payment:
    """
    Create or resume a payment intent. Idempotent — calling with the same
    idempotency_key returns the existing Payment without re-charging.
    """
    try:
        payment = Payment.objects.get(idempotency_key=idempotency_key)
        if payment.status == Payment.STATUS_COMPLETED:
            raise PaymentAlreadyCompletedError(payment)
        if payment.status == Payment.STATUS_PROCESSING:
            raise PaymentInProgressError()
        # PENDING or FAILED — return existing so client can retry confirm
        return payment
    except Payment.DoesNotExist:
        pass

    # Compute total from cart snapshot
    amount = sum(Decimal(str(item['price'])) for item in cart_items)
    from django.conf import settings as django_settings
    provider = getattr(django_settings, 'PAYMENT_GATEWAY', 'stripe')
    gateway = get_gateway(provider)
    intent = gateway.create_intent(
        amount=float(amount),
        currency='usd',
        metadata={'user_id': user.id, 'idempotency_key': idempotency_key},
    )

    payment = Payment.objects.create(
        idempotency_key=idempotency_key,
        user=user,
        amount=amount,
        currency='usd',
        status=Payment.STATUS_PENDING,
        gateway=provider,
        gateway_ref=intent['id'],
        payload={'cart': cart_items, 'gateway_intent': intent},
    )
    return payment


def confirm_payment(payment_id: str, payment_method: dict) -> Payment:
    """
    Confirm a PENDING payment. Uses select_for_update to prevent race conditions
    if the user double-clicks or submits from two tabs simultaneously.
    """
    with transaction.atomic():
        try:
            payment = Payment.objects.select_for_update().get(id=payment_id)
        except Payment.DoesNotExist:
            raise ValueError('Payment not found.')

        if payment.status == Payment.STATUS_COMPLETED:
            return payment  # idempotent — already done, just return

        if payment.status == Payment.STATUS_PROCESSING:
            raise PaymentInProgressError()

        if payment.status == Payment.STATUS_FAILED:
            raise ValueError('Payment has already failed. Please start a new checkout.')

        # Transition to PROCESSING atomically
        payment.status = Payment.STATUS_PROCESSING
        payment.save(update_fields=['status', 'updated_at'])

    # Charge outside the lock (gateway call can be slow)
    gateway = get_gateway(payment.gateway)
    result = gateway.confirm_intent(payment.gateway_ref, payment_method)

    with transaction.atomic():
        payment = Payment.objects.select_for_update().get(id=payment_id)
        if result.get('status') == 'succeeded':
            payment.status = Payment.STATUS_COMPLETED
            payment.save(update_fields=['status', 'updated_at'])
            _grant_access(payment)
        else:
            payment.status = Payment.STATUS_FAILED
            payment.error_detail = result.get('error', 'Unknown error')
            payment.save(update_fields=['status', 'error_detail', 'updated_at'])

    return payment


def _grant_access(payment: Payment):
    """
    After a successful payment, grant course access or activate a subscription.
    Reads the cart snapshot stored in payment.payload.
    """
    from apps.courses.models import Course, UserCourseAccess
    from apps.subscriptions.models import Plan, UserSubscription

    cart = payment.payload.get('cart', [])
    now = timezone.now()

    for item in cart:
        if item['item_type'] == 'course':
            course_id = item.get('course_id')
            if course_id:
                UserCourseAccess.objects.get_or_create(
                    user=payment.user,
                    course_id=course_id,
                    defaults={'payment': payment},
                )
        elif item['item_type'] == 'plan':
            plan_id = item.get('plan_id')
            if plan_id:
                try:
                    plan = Plan.objects.get(id=plan_id)
                except Plan.DoesNotExist:
                    continue
                # Deactivate any previous subscription
                UserSubscription.objects.filter(user=payment.user, is_active=True).update(is_active=False)
                UserSubscription.objects.create(
                    user=payment.user,
                    plan=plan,
                    start_date=now,
                    end_date=now + timedelta(days=plan.duration_days),
                    is_active=True,
                    payment=payment,
                )
