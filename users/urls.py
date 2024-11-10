from django.urls import path
from .views import TeacherListCreateView, TeacherDetailView, StudentListCreateView, StudentDetailView

urlpatterns = [
    path('teachers/', TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('teachers/<str:teacher_email>/', TeacherDetailView.as_view(), name='teacher-detail'),
    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<str:student_email>/', StudentDetailView.as_view(), name='student-detail'),
]