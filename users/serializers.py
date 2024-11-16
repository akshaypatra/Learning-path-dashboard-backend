from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from db_connection import db
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from bson import ObjectId
from .models import BaseUser

# BaseUser Serializer
class BaseUserSerializer(serializers.Serializer):
    role = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, max_length=128)

    def validate_password(self, value):
        # Ensure the password is hashed before saving
        if not value.startswith('pbkdf2'):
            return make_password(value)
        return value

    def create(self, validated_data):
        # Hash the password if not already hashed
        validated_data['password'] = self.validate_password(validated_data['password'])
        return validated_data

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = self.validate_password(validated_data['password'])
        return super().update(instance, validated_data)


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
        validated_data['password'] = self.validate_password(validated_data['password'])
        db["teachers"].insert_one(validated_data)
        return validated_data


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
        validated_data['password'] = self.validate_password(validated_data['password'])
        db["students"].insert_one(validated_data)
        return validated_data


# Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Check if the user is in the students collection
        user = db["students"].find_one({"email": email})
        role = "student" if user else None

        # If the user is not found in students, check teachers collection
        if not user:
            user = db["teachers"].find_one({"email": email})
            role = "teacher" if user else None

        # If no user found, raise authentication error
        if not user:
            raise AuthenticationFailed("Invalid email or password.")

        # Verify the password for the found user
        if not check_password(password, user["password"]):
            raise AuthenticationFailed("Invalid email or password.")

        # Convert the user_id to a string if it's an ObjectId
        user_id = str(user["_id"]) if isinstance(user["_id"], ObjectId) else str(user["_id"])

        # For now, we pass the user data along with the role.
        user_instance = BaseUser(
            role=role, 
            name=user["name"], 
            email=user["email"], 
            password=user["password"],
            user_id=user_id  
        )

        # Generate the JWT token
        token_data = user_instance.generate_jwt_token()

        # Return the user data along with the access and refresh tokens
        user_data = {
            "id": user_id,
            "email": user["email"],
            "role": role,
            "token": token_data['access'],
            "refresh_token": token_data['refresh']
        }

        return user_data
    
   