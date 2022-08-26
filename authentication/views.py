from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.add_message(request, messages.SUCCESS, 'Nice to see you!')
            return redirect('home')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid username or password!')
        
    return render(request, 'authentication/login.html')


def register_user(request):
    form = CustomUserCreationForm()
    errors = []
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.add_message(request, messages.SUCCESS, 'You have successfully registered! Nice to see you!')
            return redirect('home')
        else:
            for field in form.errors:
               errors.append(form.errors[field].as_text().strip('* '))
            
    return render(request, 'authentication/register.html', {'form': form, 'errors': errors})


def logout_user(request):
    logout(request)
    return redirect('login-user')