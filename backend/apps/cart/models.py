from django.db import models
from django.conf import settings
from apps.courses.models import Course
from apps.subscriptions.models import Plan


class CartItem(models.Model):
    ITEM_TYPE_COURSE = 'course'
    ITEM_TYPE_PLAN = 'plan'
    ITEM_TYPE_CHOICES = [
        (ITEM_TYPE_COURSE, 'Course'),
        (ITEM_TYPE_PLAN, 'Subscription Plan'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'cart'
        # Prevent duplicate cart entries
        unique_together = [('user', 'course'), ('user', 'plan')]

    @property
    def price(self):
        if self.item_type == self.ITEM_TYPE_COURSE and self.course:
            return self.course.price
        if self.item_type == self.ITEM_TYPE_PLAN and self.plan:
            return self.plan.price
        return 0
