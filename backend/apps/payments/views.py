from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import InitiatePaymentSerializer, ConfirmPaymentSerializer, PaymentSerializer
from .services import initiate_payment, confirm_payment, PaymentInProgressError, PaymentAlreadyCompletedError
from .models import Payment


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate(request):
    serializer = InitiatePaymentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        payment = initiate_payment(
            user=request.user,
            cart_items=data['cart_items'],
            idempotency_key=data['idempotency_key'],
        )
    except PaymentAlreadyCompletedError as e:
        return Response({
            'status': 'completed',
            'payment': PaymentSerializer(e.payment).data,
        }, status=status.HTTP_200_OK)
    except PaymentInProgressError:
        return Response({'status': 'processing'}, status=status.HTTP_202_ACCEPTED)

    return Response({
        'status': payment.status.lower(),
        'payment': PaymentSerializer(payment).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm(request):
    serializer = ConfirmPaymentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    # Verify this payment belongs to the requesting user
    try:
        payment_obj = Payment.objects.get(id=data['payment_id'], user=request.user)
    except Payment.DoesNotExist:
        return Response({'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        payment = confirm_payment(
            payment_id=str(data['payment_id']),
            payment_method={
                'card_number': data['card_number'],
                'card_expiry': data['card_expiry'],
                'card_cvc': data['card_cvc'],
                'card_name': data['card_name'],
            },
        )
    except PaymentInProgressError:
        return Response({'status': 'processing'}, status=status.HTTP_202_ACCEPTED)
    except ValueError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    http_status = status.HTTP_200_OK if payment.status == Payment.STATUS_COMPLETED else status.HTTP_402_PAYMENT_REQUIRED
    return Response({
        'status': payment.status.lower(),
        'payment': PaymentSerializer(payment).data,
    }, status=http_status)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, pk):
    try:
        payment = Payment.objects.get(id=pk, user=request.user)
    except Payment.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response({
        'status': payment.status.lower(),
        'payment': PaymentSerializer(payment).data,
    })
