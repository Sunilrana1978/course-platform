from django.urls import path
from .views import CourseListView, CourseDetailView, course_access

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('<int:pk>/access/', course_access, name='course-access'),
]
