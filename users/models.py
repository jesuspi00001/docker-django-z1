from django.db import models

class User(models.Model):
    username = models.CharField(max_length=255, unique=True, error_messages={'unique': 'Esta dirección de correo electrónico ya está en uso.'})
    email = models.EmailField()
    password = models.CharField(max_length=25)

    def __str__(self):
        return self.username