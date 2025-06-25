from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    ROLE_CHOICES=(('admin','Admin'),
                  ('employee','Emplyoee'),)
    
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    role=models.CharField(max_length=20,choices=ROLE_CHOICES,default='employee')
    name=models.CharField(max_length=20)
    email=models.EmailField(null=False)
    address=models.CharField(max_length=100)
    phone=models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    


class Task(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()
    assigned_to=models.ForeignKey(User,on_delete=models.CASCADE,related_name='tasks')
    assigned_by=models.ForeignKey(User,on_delete=models.CASCADE,related_name='assigned_tasks')
    created_at=models.DateTimeField(auto_now_add=True)
    is_completed=models.BooleanField(default=False)


class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')
    message=models.CharField(max_length=500)
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)   
