from django.db import models


class User(models.Model):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("admin", "Admin"),
        ("parent", "Parent"),
    )

    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    mobile = models.CharField(max_length=10)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class OTP(models.Model):
    SEND_TYPE_CHOICES = (
        ("mobile", "Mobile"),
        ("email", "Email"),
    )

    SEND_FOR_CHOICES = (
        ("verification", "Verification"),
        ("forgot", "Forgot Password"),
    )

    send_by = models.CharField(max_length=100)  # mobile or email
    send_type = models.CharField(max_length=10, choices=SEND_TYPE_CHOICES)
    send_for = models.CharField(max_length=20, choices=SEND_FOR_CHOICES)

    otp = models.IntegerField()
    created_at = models.IntegerField()  # Unix timestamp

    def __str__(self):
        return f"{self.send_by} - {self.otp}"