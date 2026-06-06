from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CartItem
from .serializers import CartItemSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_detail(request):
    items = CartItem.objects.filter(user=request.user).select_related('course', 'plan')
    serializer = CartItemSerializer(items, many=True, context={'request': request})
    total = sum(item.price for item in items)
    return Response({'items': serializer.data, 'total': str(total)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item(request):
    serializer = CartItemSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    try:
        item = serializer.save()
    except Exception:
        return Response({'detail': 'Item already in cart.'}, status=status.HTTP_409_CONFLICT)
    return Response(CartItemSerializer(item, context={'request': request}).data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_item(request, pk):
    try:
        item = CartItem.objects.get(pk=pk, user=request.user)
    except CartItem.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
