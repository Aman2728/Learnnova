from django.db import models

# Create your models here.


from django.db import models
from apps.courses.models import Course
from apps.users.models import User


class Assignment(models.Model):

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_assignments"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    link = models.URLField(null=True, blank=True)

    title = models.CharField(max_length=200)

    description = models.TextField()

    language = models.CharField(max_length=50)  
    # example: C, C++, Python, Java

    due_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    


class AssignmentSubmission(models.Model):

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    file = models.FileField(upload_to="submissions/")

    submitted_at = models.DateTimeField(auto_now_add=True)

    score = models.IntegerField(null=True, blank=True)

    feedback = models.TextField(null=True, blank=True)