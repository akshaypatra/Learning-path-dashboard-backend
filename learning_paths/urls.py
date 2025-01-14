from django.urls import path
from .views import LearningPathView

urlpatterns = [
    path('', LearningPathView.as_view(), name='learning-paths'),
    path('<str:pk>/', LearningPathView.as_view(), name='learning-path-detail'),
]
