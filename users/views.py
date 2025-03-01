from .serializers import TeacherSerializer, StudentSerializer, LoginSerializer
from db_connection import db
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import BaseUser
import jwt
from django.conf import settings

from rest_framework.permissions import IsAuthenticated

class TeacherListCreateView(APIView):
    """
    Handles listing all teachers and creating a new teacher.
    """
    def get(self, request, format=None):
        teachers = list(db["teachers"].find({}, {"_id": 0}))  # Avoid returning MongoDB _id field
        return Response(teachers, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            teacher_data = serializer.validated_data

            # Check for duplicates in email or employee ID
            duplicate_email = db["teachers"].find_one({"email": teacher_data["email"]})
            duplicate_employee_id = db["teachers"].find_one({"employeeID": teacher_data["employeeID"]})

            if duplicate_email:
                return Response(
                    {"error": "A teacher with this email already exists.", "data": duplicate_email},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if duplicate_employee_id:
                return Response(
                    {"error": "A teacher with this employee ID already exists.", "data": duplicate_employee_id},
                    status=status.HTTP_400_BAD_REQUEST
                )

            db["teachers"].insert_one(teacher_data)  # Save the teacher
            return Response(
                {
                    "message": "Teacher account created successfully.",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherDetailView(APIView):
    """
    Handles retrieving, updating, and deleting a single teacher.
    """
    def get(self, request, teacher_email, format=None):
        teacher = db["teachers"].find_one({"email": teacher_email}, {"_id": 0})
        if teacher:
            return Response(teacher, status=status.HTTP_200_OK)
        return Response({"detail": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, teacher_email, format=None):
        teacher = db["teachers"].find_one({"email": teacher_email})
        if not teacher:
            return Response({"detail": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            updated_teacher = serializer.validated_data
            db["teachers"].update_one({"email": teacher_email}, {"$set": updated_teacher})
            return Response(updated_teacher, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, teacher_email, format=None):
        result = db["teachers"].delete_one({"email": teacher_email})
        if result.deleted_count > 0:
            return Response({"detail": "Teacher deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND)


class StudentListCreateView(APIView):
    """
    Handles listing all students and creating a new student.
    """
    def get(self, request, format=None):
        students = list(db["students"].find({}, {"_id": 0}))  # Avoid returning MongoDB _id field
        return Response(students, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            student_data = serializer.validated_data

            # Check for duplicates in email or enrollment number
            duplicate_email = db["students"].find_one({"email": student_data["email"]})
            duplicate_enrollment_number = db["students"].find_one({"enrollmentNumber": student_data["enrollmentNumber"]})

            if duplicate_email:
                return Response(
                    {"error": "A student with this email already exists.", "data": duplicate_email},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if duplicate_enrollment_number:
                return Response(
                    {"error": "A student with this enrollment number already exists.", "data": duplicate_enrollment_number},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            

            db["students"].insert_one(student_data)  # Save the student
            return Response(
                {
                    "message": "Student account created successfully.",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentDetailView(APIView):
    """
    Handles retrieving, updating, and deleting a single student.
    """
    def get(self, request, student_email, format=None):
        student = db["students"].find_one({"email": student_email}, {"_id": 0})
        if student:
            return Response(student, status=status.HTTP_200_OK)
        return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, student_email, format=None):
        student = db["students"].find_one({"email": student_email})
        if not student:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            updated_student = serializer.validated_data
            db["students"].update_one({"email": student_email}, {"$set": updated_student})
            return Response(updated_student, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, student_email, format=None):
        result = db["students"].delete_one({"email": student_email})
        if result.deleted_count > 0:
            return Response({"detail": "Student deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)



class LoginView(APIView):
    """
    Handles user login.
    """

    def post(self, request, format=None):
        # Deserialize the incoming request data using the LoginSerializer
       
        serializer = LoginSerializer(data=request.data)
        
        # Check if the serializer data is valid
        if serializer.is_valid():
            # Get the validated user data
            user_data = serializer.validated_data  # Contains user info and token

            # Return a successful response with token and role
            return Response(
                {
                    "message": "Login successful",
                    "access_token": user_data['access_token'],  
                    "refresh_token": user_data['refresh_token'],
                    "role": user_data.get("role", "user"),  # Role (e.g., 'teacher', 'student')
                    "employeeID":user_data.get("employeeID", None),
                    "classID":user_data.get("classID",None)
                },
                status=status.HTTP_200_OK
            )
        
        # If serializer is invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UpdateClassIDView(APIView):
    def get_user_from_token(self, request):
        """Extracts and decodes JWT token manually."""
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return None, Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = auth_header.split(" ")[1]  # Extract token after 'Bearer'
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return payload, None  # Return payload data if valid
        except jwt.ExpiredSignatureError:
            return None, Response({"error": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return None, Response({"error": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, format=None):
        """Updates the student's classID if valid."""
        # Decode user from JWT
        payload, error_response = self.get_user_from_token(request)
        if error_response:
            return error_response  # Return authentication error

        student_email = payload.get("email")  # Get student email from token
        if not student_email:
            return Response({"error": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)

        new_class_id = request.data.get("classID")  # Get new classID from request

        if not new_class_id:
            return Response({"error": "ClassID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if student exists in MongoDB
        student = db["students"].find_one({"email": student_email})
        if not student:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate if the classID exists in learning_path
        class_exists = db["learning_paths"].find_one({"classID": new_class_id})
        if not class_exists:
            return Response({"error": "Invalid classID. No class found in learning_path."}, status=status.HTTP_404_NOT_FOUND)

        # Update the classID in the student's record
        db["students"].update_one({"email": student_email}, {"$set": {"classID": new_class_id}})

        return Response({"message": f"ClassID updated to {new_class_id} successfully."}, status=status.HTTP_200_OK)
