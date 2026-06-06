from django.core.management.base import BaseCommand
from apps.courses.models import Course
from apps.subscriptions.models import Plan

COURSES = [
    # Web Development
    {'title': 'HTML & CSS Fundamentals', 'description': 'Master the building blocks of the web.', 'price': '29.99', 'category': 'web', 'instructor': 'Alice Johnson', 'duration_hours': 12, 'thumbnail_url': 'https://picsum.photos/seed/html/400/225'},
    {'title': 'JavaScript Essentials', 'description': 'Learn modern JavaScript from scratch.', 'price': '49.99', 'category': 'web', 'instructor': 'Alice Johnson', 'duration_hours': 20, 'thumbnail_url': 'https://picsum.photos/seed/js/400/225'},
    {'title': 'React for Beginners', 'description': 'Build interactive UIs with React 18.', 'price': '59.99', 'category': 'web', 'instructor': 'Bob Smith', 'duration_hours': 25, 'thumbnail_url': 'https://picsum.photos/seed/react/400/225'},
    {'title': 'Full-Stack with Django & React', 'description': 'End-to-end web app development.', 'price': '79.99', 'category': 'web', 'instructor': 'Bob Smith', 'duration_hours': 40, 'thumbnail_url': 'https://picsum.photos/seed/django/400/225'},
    # Data Science
    {'title': 'Python for Data Science', 'description': 'NumPy, Pandas, and Matplotlib from scratch.', 'price': '49.99', 'category': 'data', 'instructor': 'Carol White', 'duration_hours': 18, 'thumbnail_url': 'https://picsum.photos/seed/python/400/225'},
    {'title': 'Machine Learning Fundamentals', 'description': 'Supervised and unsupervised learning algorithms.', 'price': '69.99', 'category': 'data', 'instructor': 'Carol White', 'duration_hours': 30, 'thumbnail_url': 'https://picsum.photos/seed/ml/400/225'},
    {'title': 'Deep Learning with PyTorch', 'description': 'Neural networks and modern deep learning.', 'price': '89.99', 'category': 'data', 'instructor': 'David Lee', 'duration_hours': 35, 'thumbnail_url': 'https://picsum.photos/seed/dl/400/225'},
    # DevOps
    {'title': 'Docker & Containers', 'description': 'Containerise every application you build.', 'price': '44.99', 'category': 'devops', 'instructor': 'Eva Martinez', 'duration_hours': 15, 'thumbnail_url': 'https://picsum.photos/seed/docker/400/225'},
    {'title': 'Kubernetes in Production', 'description': 'Orchestrate containers at scale.', 'price': '74.99', 'category': 'devops', 'instructor': 'Eva Martinez', 'duration_hours': 28, 'thumbnail_url': 'https://picsum.photos/seed/k8s/400/225'},
    {'title': 'CI/CD with GitHub Actions', 'description': 'Automate testing and deployment pipelines.', 'price': '39.99', 'category': 'devops', 'instructor': 'Frank Chen', 'duration_hours': 10, 'thumbnail_url': 'https://picsum.photos/seed/cicd/400/225'},
]

PLANS = [
    {'name': 'Monthly', 'price': '29.00', 'duration_days': 30, 'description': 'Unlimited access to all courses for 30 days.'},
    {'name': 'Annual', 'price': '199.00', 'duration_days': 365, 'description': 'Best value — unlimited access for a full year.'},
]


class Command(BaseCommand):
    help = 'Seed courses and subscription plans'

    def handle(self, *args, **kwargs):
        for data in COURSES:
            Course.objects.get_or_create(title=data['title'], defaults=data)
        self.stdout.write(f'  Seeded {len(COURSES)} courses.')

        for data in PLANS:
            Plan.objects.get_or_create(name=data['name'], defaults=data)
        self.stdout.write(f'  Seeded {len(PLANS)} subscription plans.')

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
