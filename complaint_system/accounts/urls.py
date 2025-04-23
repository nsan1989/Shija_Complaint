from django.urls import path
from .views import Register, Login, Profile, DepartmentView, StaffView, AdminView, SuperAdminView, UsersView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', Register, name='register'),
    path('login/', Login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('staff/dashboard/', StaffView, name='staff'),
    path('incharge/dashboard/', AdminView, name='staff_admin'),
    path('super_admin/dashboard/', SuperAdminView, name='super_admin'),
    path('staff/profile_details/', Profile, name='staff_profile'),
    path('incharge/profile_details/', Profile, name='incharge_profile'),
    path('super_admin/profile_details/', Profile, name='super_admin_profile'),
    path('departments/', DepartmentView, name='departments'),
    path('all_users/', UsersView, name='all_users'),
]
