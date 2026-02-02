from django.urls import path
from .views import (RegisterTeacherView, 
    ProfileView,
    SchoolClassCreateView,
    SchoolClassListView,
    SchoolClassDetailView,
    SchoolClassUpdateView,
    SchoolClassDeleteView,
)
urlpatterns = [
    path('register-teacher/', RegisterTeacherView.as_view(), name='register_teacher'),
    path('profile/', ProfileView.as_view(), name='profile'),
    # Phase 2 - Class Module
    path('classes/create/', SchoolClassCreateView.as_view(), name='class_create'),
    path('classes/', SchoolClassListView.as_view(), name='class_list'),
    path('classes/<int:pk>/', SchoolClassDetailView.as_view(), name='class_detail'),
    path('classes/<int:pk>/update/', SchoolClassUpdateView.as_view(), name='class_update'),
    path('classes/<int:pk>/delete/', SchoolClassDeleteView.as_view(), name='class_delete'),
]
