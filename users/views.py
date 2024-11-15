from .serializers import TeacherSerializer, StudentSerializer
from db_connection import db
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

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
            duplicate_employee_id = db["teachers"].find_one({"employeeId": teacher_data["employeeID"]})

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


