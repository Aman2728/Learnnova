from django.db import models
from django.utils import timezone

# Create your models here.


from django.db import models
from apps.users.models import User


class Attendance(models.Model):

    STATUS_CHOICES = (
        ("present", "Present"),
        ("absent", "Absent"),
    )

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_attendance")
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="present")
    marked_at = models.DateTimeField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)   # 👈 ADD THIS

    def __str__(self):
        return f"{self.teacher.name} - {self.date}"




from django.db import models
from apps.users.models import User

class StudentAttendance(models.Model):

    STATUS_CHOICES = (
        ("present","Present"),
        ("absent","Absent")
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role":"student"}
    )

    date = models.DateField(auto_now_add=True)

    time = models.TimeField(auto_now_add=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="present"
    )

    def __str__(self):
        return f"{self.student.username} - {self.date}"