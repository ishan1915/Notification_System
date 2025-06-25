from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Task,EmployeeGroup

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class TaskAssignmentForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # filter only employees
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    group = forms.ModelChoiceField(
        queryset=EmployeeGroup.objects.none(),  # set dynamically in view
        required=False,
        empty_label="--- Select Group (Optional) ---"
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'group', 'users']
