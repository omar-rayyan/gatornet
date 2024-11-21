from django.urls import path
from social_app import views

urlpatterns = [
    path('', views.root, name='root'),
    path('home', views.home, name='home'),
    path('post/<int:id>', views.view_post, name='view_post'),
    path('profile/<int:id>', views.view_profile, name='view_profile'),
    path('edit_profile', views.view_edit_profile_page, name='view_edit_profile_page'),
    path('edit_profile_confirm', views.update_profile, name='edit_profile'),
    path('dviewpost', views.dviewpost),
    
]