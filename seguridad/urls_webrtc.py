# seguridad/urls_webrtc.py - URLs para WebRTC
from django.urls import path
from . import views_webrtc

urlpatterns = [
    path('status/', views_webrtc.webrtc_status, name='webrtc_status'),
    path('test/', views_webrtc.webrtc_test, name='webrtc_test'),
    path('face/', views_webrtc.webrtc_face_recognition, name='webrtc_face'),
    path('mobile/', views_webrtc.mobile_camera_interface, name='mobile_camera'),
]