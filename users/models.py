from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True, error_messages={'unique': 'Esta dirección de correo electrónico ya está en uso.'})
    email = models.EmailField()
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username