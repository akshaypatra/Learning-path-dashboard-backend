from .serializers import TeacherSerializer, StudentSerializer
from db_connection import db
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class TeacherListCreateView(APIView):
    def get(self, request, format=None):
        teachers = db["teachers"].find()
        teachers_list = list(teachers)
        return Response(teachers_list)

    def post(self, request, format=None):
        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            teacher_data = serializer.validated_data
            db["teachers"].insert_one(teacher_data)  # Save to MongoDB
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherDetailView(APIView):
    def get(self, request, teacher_email, format=None):
        teacher = db["teachers"].find_one({"email": teacher_email})
        if teacher:
            return Response(teacher)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, teacher_email, format=None):
        teacher = db["teachers"].find_one({"email": teacher_email})
        if not teacher:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            updated_teacher = serializer.update(teacher, serializer.validated_data)
            db["teachers"].update_one({"email": teacher_email}, {"$set": updated_teacher})
            return Response(updated_teacher)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentListCreateView(APIView):
    def get(self, request, format=None):
        students = db["students"].find()
        students_list = list(students)
        return Response(students_list)

    def post(self, request, format=None):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            student_data = serializer.validated_data
            db["students"].insert_one(student_data)  # Save to MongoDB
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentDetailView(APIView):
    def get(self, request, student_email, format=None):
        student = db["students"].find_one({"email": student_email})
        if student:
            return Response(student)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, student_email, format=None):
        student = db["students"].find_one({"email": student_email})
        if not student:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            updated_student = serializer.update(student, serializer.validated_data)
            db["students"].update_one({"email": student_email}, {"$set": updated_student})
            return Response(updated_student)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)