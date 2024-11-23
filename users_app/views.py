from django.shortcuts import render, redirect
from users_app.models import User
from django.contrib import messages

def root(request):
    if 'user_id' in request.session:
        return redirect('home')
    return redirect('view_login_page')
def view_login_page(request):
    if 'user_id' in request.session:
        return redirect('home')
    return render(request, 'login.html')
def view_registration_page(request):
    if 'user_id' in request.session:
        return redirect('home')
    return render(request, 'register.html')
def login(request):
    errors = User.objects.login_validator(request.POST)
    if errors:
        for key, value in errors.items():
            messages.error(request, value, extra_tags='login')
        request.session['loginform'] = request.POST
        return redirect('/')
    user = User.objects.get(email=request.POST['email'])
    request.session['user_id'] = user.id
    request.session['first_name'] = user.first_name
    request.session['last_name'] = user.last_name
    return redirect('home')
def register(request):
    errors = User.objects.registration_validator(request.POST)
    if errors:
        for key, value in errors.items():
            messages.error(request, value, extra_tags='register')
        request.session['registerform'] = request.POST
        return redirect('view_registration_page')
    user = User.objects.create_user(request.POST)
    request.session['user_id'] = user.id
    request.session['first_name'] = user.first_name
    request.session['last_name'] = user.last_name
    return redirect('home')
def logout(request):
    request.session.clear()
    return redirect('/')