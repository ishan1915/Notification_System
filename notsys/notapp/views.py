from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from  .serializers import SignupSerializer , TaskSerializer, NotificationSerializer, GroupSerializer

from .forms import SignUpForm, TaskAssignmentForm
from .models import EmployeeGroup, Task, Notification, Profile
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status



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







########Api views##################
@api_view(['POST'])
@permission_classes([AllowAny])

def login_view(request):
    username=request.data.get('username')
    password=request.data.get('password')

    user=authenticate(request,username=username,password=password)
    if user is not None:
        login(request,user)
        role=user.profile.role

        if role=='admin':
            redirect_to='admin_dashboard'

        else:
            redirect_to='employee_dashboard'

        return Response({
            "message":"Login Successful",
            "role":role,
            "redirect":redirect_to
        },status=status.HTTP_200_OK)        
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view1(request):
    serializer=SignupSerializer(data=request.data)
    if serializer.is_valid():
        user=serializer.save()
         
        login(request, user)
        return Response({"message": "Signup successful"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view1(request):
    logout(request)
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard1(request):
    role = request.user.profile.role
    if role == 'admin':
        return Response({"redirect": "admin_dashboard1"})
    else:
        return Response({"redirect": "employee_dashboard1"})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_dashboard1(request):
    if request.user.profile.role != 'admin':
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(created_by=request.user)
            users = serializer.validated_data.get('users', [])
            group = serializer.validated_data.get('group')

            if group:
                for user in group.members.all():
                    task.assigned_to.add(user)
            for user in users:
                task.assigned_to.add(user)

            for user in task.assigned_to.all():
                Notification.objects.create(user=user, message=f"New Task: {task.title}")

            return Response({"message": "Task assigned"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    tasks = Task.objects.filter(created_by=request.user)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_dashboard1(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    task_serializer = TaskSerializer(tasks, many=True)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    notif_serializer = NotificationSerializer(notifications, many=True)
    return Response({
        "tasks": task_serializer.data,
        "notifications": notif_serializer.data,
        "unread_count": unread_count
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_read1(request, not_id):
    noti = get_object_or_404(Notification, id=not_id, user=request.user)
    noti.is_read = True
    noti.save()
    return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)

