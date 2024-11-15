from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from db_connection import db
from rest_framework.exceptions import ValidationError

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

    def validate_email(self, value):
        # Check if the email already exists for a teacher
        existing_teacher = db["teachers"].find_one({"email": value})
        if existing_teacher:
            raise ValidationError("A teacher with this email already exists.")
        return value

    def validate_employeeID(self, value):
        # Check if the employeeID already exists for a teacher
        existing_teacher = db["teachers"].find_one({"employeeID": value})
        if existing_teacher:
            raise ValidationError("A teacher with this employee ID already exists.")
        return value

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

    def validate_email(self, value):
        # Check if the email already exists for a student
        existing_student = db["students"].find_one({"email": value})
        if existing_student:
            raise ValidationError("A student with this email already exists.")
        return value

    def validate_enrollmentNumber(self, value):
        # Check if the enrollmentNumber already exists for a student
        existing_student = db["students"].find_one({"enrollmentNumber": value})
        if existing_student:
            raise ValidationError("A student with this enrollment number already exists.")
        return value

    def create(self, validated_data):
        validated_data['role'] = 'student'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['role'] = 'student'
        return super().update(instance, validated_data)
