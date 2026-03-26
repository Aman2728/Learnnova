from django.db import models
from apps.users.models import User


class Course(models.Model):

    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("completed", "Completed"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    duration_in_days = models.IntegerField(default=0)

    total_slots = models.IntegerField(default=0)
    remaining_slots = models.IntegerField(default=0)

    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_courses"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_courses"
    )

    teacher_assigned_at = models.DateTimeField(null=True, blank=True)

    students = models.ManyToManyField(
        User,
        blank=True,
        related_name="enrolled_courses"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title