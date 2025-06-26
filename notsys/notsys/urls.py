"""
URL configuration for notsys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from notapp.views import admin_dashboard1, dashboard1, employee_dashboard1, login_view, logout_view, logout_view1, mark_read, mark_read1, signup_view, admin_dashboard, employee_dashboard, dashboard, signup_view1
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', logout_view, name='logout'),

    path('signup/', signup_view, name='signup'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('employee-dashboard/', employee_dashboard, name='employee_dashboard'),
    path('mark-read/<int:not_id>/', mark_read, name='mark_read'),

    path('', dashboard, name='dashboard'),



    ####API URLS####
    path('login1/', login_view, name='login'),
    path('signup1/',signup_view1,name='signup1'),
    path('logout/', logout_view1, name='logout'),
    path('admin-dashboard1/', admin_dashboard1, name='admin_dashboard1'),
    path('employee-dashboard1/', employee_dashboard1, name='employee_dashboard1'),
    path('mark-read1/<int:not_id>/', mark_read1, name='mark_read1'),
    path('', dashboard1, name='dashboard1'),






 ]
