from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class UserMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField(null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    
    
class Notification(models.Model):
    user= models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000, null=True)
    