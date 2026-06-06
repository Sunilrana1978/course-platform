from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Course
from .serializers import CourseSerializer


class CourseListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Course.objects.all()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        if category:
            qs = qs.filter(category=category)
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_access(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=404)

    has_direct = course.accesses.filter(user=request.user).exists()
    if has_direct:
        return Response({'has_access': True, 'reason': 'purchased'})

    from apps.subscriptions.models import UserSubscription
    sub = UserSubscription.objects.filter(
        user=request.user, is_active=True, end_date__gt=timezone.now()
    ).first()
    if sub:
        return Response({'has_access': True, 'reason': 'subscription', 'plan': sub.plan.name})

    return Response({'has_access': False})
