from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from social_app import views

urlpatterns = [
    path('', include('users_app.urls')),
    path('social/', include('social_app.urls')),
    path('get_messages/<int:friend_id>/', views.get_messages, name='get_messages'),
    path('send_message/', views.send_message, name='send_message'),
    path('update_activity/', views.update_activity, name='update_activity'),
    path('about_us', views.about_us, name='about_us'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
