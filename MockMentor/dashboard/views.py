from django.shortcuts import render


def home(request):
    return render(request, 'dashboard/home.html')


def takeInterview(request):
    return render(request, 'dashboard/takeInterview.html')
