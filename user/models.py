from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    # Новые поля:
    city = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"