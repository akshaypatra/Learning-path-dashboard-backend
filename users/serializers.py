

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from db_connection import db

# BaseUser Serializer
class BaseUserSerializer(serializers.Serializer):
    role = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return validated_data

    def update(self, instance, validated_data):
        instance['role'] = validated_data.get('role', instance['role'])
        instance['name'] = validated_data.get('name', instance['name'])
        instance['email'] = validated_data.get('email', instance['email'])
        instance['password'] = validated_data.get('password', instance['password'])
        return instance

# Teacher Serializer
class TeacherSerializer(BaseUserSerializer):
    employeeID = serializers.CharField(max_length=20)

    def create(self, validated_data):
        validated_data['role'] = 'teacher'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['role'] = 'teacher'
        return super().update(instance, validated_data)

# Student Serializer
class StudentSerializer(BaseUserSerializer):
    enrollmentNumber = serializers.CharField(max_length=20)
    department = serializers.CharField(max_length=100)

    def create(self, validated_data):
        validated_data['role'] = 'student'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['role'] = 'student'
        return super().update(instance, validated_data)