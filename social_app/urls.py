from django.urls import path
from social_app import views

urlpatterns = [
    path('', views.root, name='root'),
    path('home', views.home, name='home'),
    path('post/<int:id>', views.view_post, name='view_post'),
    path('profile/<int:id>', views.view_profile, name='view_profile'),
]