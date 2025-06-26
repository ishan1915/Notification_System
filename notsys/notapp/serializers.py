from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile,Task,Notification,EmployeeGroup

class SignupSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES)
    password = serializers.CharField(write_only=True)
    name = serializers.CharField()
    phone = serializers.IntegerField()
    address = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role', 'name', 'phone', 'address']

    def create(self, validated_data):
        role = validated_data.pop('role')
        name = validated_data.pop('name')
        phone = validated_data.pop('phone')
        address = validated_data.pop('address')
        email = validated_data.get('email')

        user = User.objects.create(
            username=validated_data['username'],
            email=email
        )
        user.set_password(validated_data['password'])
        user.save()

        Profile.objects.create(
            user=user,
            role=role,
            name=name,
            email=email,
            phone=phone,
            address=address
        )

        return user

    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = EmployeeGroup
        fields = ['id', 'name', 'members']


class TaskSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    group = serializers.PrimaryKeyRelatedField(queryset=EmployeeGroup.objects.all(), required=False)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'users', 'group', 'created_by', 'created_at']

    def create(self, validated_data):
        users = validated_data.pop('users', [])
        group = validated_data.pop('group', None)
        task = Task.objects.create(**validated_data)
        task.assigned_to.set(users)
        return task


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']
