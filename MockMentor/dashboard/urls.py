from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name="home"),
    path('takeInterview', views.takeInterview, name="takeInterview"),
    path('history', views.history, name="history"),
    path('feedback', views.feedback, name="feedback"),
    path('camera', views.getCam, name="camera"),
    path('video_feed', views.main_interview, name='video_feed'),
    path('webcam_feed/<path:key>', views.getStreaming, name='webcam_feed'),
    path('camKey', views.getCamKey, name="camKey"),
    path('checkPosition_video', views.checkPositionVideo, name="checkPosition_video"),
    path('checkPosition', views.checkPosition, name="checkPosition"),
]
