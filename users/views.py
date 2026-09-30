from django.shortcuts import render

def Register_view(request):
    return render(request, 'users/register.html')

def Login_view(request):
    return render(request, 'users/login.html')