from django.urls import path, include

urlpatterns = [
    path('', include('users_app.urls')),
]
