from django.urls import path
from users_app import views

urlpatterns = [
    path('', views.root, name='root'),
    path('login', views.view_login_page, name='view_login_page'),
    path('register', views.view_registration_page, name='view_registration_page'),
    path('confirm_register', views.register, name='register'),
    path('confirm_login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
]