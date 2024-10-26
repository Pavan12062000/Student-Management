from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('student/<int:pk>/', views.student_detail, name='student_detail'),
    path('student/new/', views.student_create, name='student_create'),
    path('student/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('student/<int:pk>/delete/', views.student_delete, name='student_delete'),  # Add this line for delete
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='user_logout'),  # Redirect to login page after logout
    path('forgot_password/', views.forgot_password, name='forgot_password'),
]
