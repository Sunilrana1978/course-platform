from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Plan, UserSubscription
from .serializers import PlanSerializer, UserSubscriptionSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def plan_list(request):
    plans = Plan.objects.all()
    return Response(PlanSerializer(plans, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_subscription(request):
    sub = UserSubscription.objects.filter(
        user=request.user, is_active=True, end_date__gt=timezone.now()
    ).select_related('plan').first()
    if not sub:
        return Response({'subscription': None})
    return Response({'subscription': UserSubscriptionSerializer(sub).data})
