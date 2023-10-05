from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True, error_messages={'unique': 'Este usuario ya existe.'})
    email = models.EmailField()
    password = models.CharField(max_length=255)
    # Campo donde almaceneramos el token unico que enviaremos en el correo para restablecer pass. 
    reset_password_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username
    

class Idea(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Cascade para borrar todas las ideas de un usuario borrado.
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('protected', 'Protected'),
        ('private', 'Private'),
    )
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public') # Este campo se usa para establecer la visibilidad de la idea.

    def __str__(self):
        return f"Idea escrita por {self.user.username}: {self.text}"


class FollowRequest(models.Model):
    requester = models.ForeignKey(User, related_name='requester_user', on_delete=models.CASCADE)
    target_user = models.ForeignKey(User, related_name='target_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, default='pending')

    class Meta:
        unique_together = ('requester', 'target_user')

    def __str__(self):
        return f'{self.requester.username} -> {self.target_user.username} ({self.status})'


class UserFollowerList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    following = models.ManyToManyField(User, related_name='followers')

    def __str__(self):
        return self.user