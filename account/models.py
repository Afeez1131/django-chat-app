from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=155)
    country = models.CharField(max_length=155, default="Nigeria")
    age = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.state}"
