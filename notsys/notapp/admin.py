from django.contrib import admin
from .models import Profile,Task,Notification,EmployeeGroup
# Register your models here.
admin.site.register(Profile)
admin.site.register(Task)
admin.site.register(Notification)
admin.site.register(EmployeeGroup)