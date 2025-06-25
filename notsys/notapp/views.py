from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .forms import SignUpForm, TaskAssignmentForm
from .models import EmployeeGroup, Task, Notification, Profile
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data.get('email')
            user.save()
            role = form.cleaned_data.get('role')
            Profile.objects.create(user=user, role=role)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})



@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  

@login_required
def dashboard(request):
    if request.user.profile.role == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('employee_dashboard')

@login_required
def admin_dashboard(request):
    # Ensure only admins can access
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role != 'admin':
        return HttpResponseForbidden("Access denied. You are not an admin.")

    # Get employee users based on Profile role
    employee_profiles = Profile.objects.filter(role='employee')
    employee_users = [p.user for p in employee_profiles]

    # Setup the form with dynamic user/group queryset
    form = TaskAssignmentForm()
    form.fields['group'].queryset = EmployeeGroup.objects.filter(admin=request.user)
    form.fields['users'].queryset = User.objects.filter(id__in=[u.id for u in employee_users])

    if request.method == 'POST':
        form = TaskAssignmentForm(request.POST)
        form.fields['group'].queryset = EmployeeGroup.objects.filter(admin=request.user)
        form.fields['users'].queryset = User.objects.filter(id__in=[u.id for u in employee_users])

        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()

            selected_users = form.cleaned_data['users']
            selected_group = form.cleaned_data['group']

            # Assign to group members if group selected
            if selected_group:
                for user in selected_group.members.all():
                    task.assigned_to.add(user)

            # Assign to manually selected users
            if selected_users:
                for user in selected_users:
                    task.assigned_to.add(user)

            # Send notifications
            for user in task.assigned_to.all():
                Notification.objects.create(user=user, message=f"New Task: {task.title}")

            return redirect('admin_dashboard')

    tasks = Task.objects.filter(created_by=request.user)
    return render(request, 'admin_dashboard.html', {'form': form, 'tasks': tasks})

@login_required
def employee_dashboard(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    unread_count = request.user.notifications.filter(is_read=False).count()
    notifications = request.user.notifications.order_by('-created_at')
    return render(request, 'employee_dashboard.html', {
        'tasks': tasks,
        'notifications': notifications,
        'unread_count': unread_count
    })

@require_POST
def mark_read(request,not_id):
    noti=get_object_or_404(Notification,id=not_id,user=request.user)
    noti.is_read=True
    noti.save()
    return redirect(employee_dashboard)