from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('user/', views.UserDetailView.as_view(), name='user-detail'),
    path('change-password/', views.change_password, name='change-password'),
    path('permissions/', views.user_permissions, name='user-permissions'),
]