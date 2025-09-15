"""
URLs for Face Recognition API
"""

from django.urls import path
from .views import (
    FaceEnrollView, FaceVerifyView, FaceDeleteView, FaceStatusView
)

app_name = 'seguridad'

urlpatterns = [
    # Face Recognition Endpoints
    path('api/faces/enroll/', FaceEnrollView.as_view(), name='face-enroll'),
    path('api/faces/verify/', FaceVerifyView.as_view(), name='face-verify'),
    path('api/faces/enroll/<int:copropietario_id>/', FaceDeleteView.as_view(), name='face-delete'),
    path('api/faces/status/<int:copropietario_id>/', FaceStatusView.as_view(), name='face-status'),
]
