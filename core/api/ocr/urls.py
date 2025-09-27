from django.urls import path

from .views import PlateOCRView


urlpatterns = [
    path('ocr/placa/', PlateOCRView.as_view(), name='ocr-placa'),
]