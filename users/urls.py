from django.urls import path
from .views import TeacherListCreateView, TeacherDetailView, StudentListCreateView, StudentDetailView,LoginView,UpdateClassIDView

urlpatterns = [
    path('teachers/', TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('teachers/<str:teacher_email>/', TeacherDetailView.as_view(), name='teacher-detail'),
    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<str:student_email>/', StudentDetailView.as_view(), name='student-detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('update_class_id/', UpdateClassIDView.as_view(), name='update-class-id'),
]



'''
Testing Endpoints

Teachers:

GET /teachers/ - List all teachers.
POST /teachers/ - Add or update a teacher.
GET /teachers/<teacher_email>/ - Retrieve a teacher.
PUT /teachers/<teacher_email>/ - Update a teacher.
DELETE /teachers/<teacher_email>/ - Delete a teacher.

Students:

GET /students/ - List all students.
POST /students/ - Add or update a student.
GET /students/<student_email>/ - Retrieve a student.
PUT /students/<student_email>/ - Update a student.
DELETE /students/<student_email>/ - Delete a student.

'''