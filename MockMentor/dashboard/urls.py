from django.urls import path
from .import views

urlpatterns = [
    path('', views.home),
    path('takeInterview', views.takeInterview)
]
