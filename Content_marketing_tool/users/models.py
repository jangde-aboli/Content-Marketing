from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    number_of_publications = models.IntegerField(default=0)

    def __str__(self):
        return self.username
