from django.db import models
from django.conf import settings


class Course(models.Model):
    CATEGORY_CHOICES = [
        ('web', 'Web Development'),
        ('data', 'Data Science'),
        ('devops', 'DevOps'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    thumbnail_url = models.URLField(blank=True)
    duration_hours = models.PositiveIntegerField(default=0)
    instructor = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'courses'

    def __str__(self):
        return self.title


class UserCourseAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_accesses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='accesses')
    granted_at = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey('payments.Payment', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'courses'
        unique_together = ('user', 'course')
