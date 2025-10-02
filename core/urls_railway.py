"""
URL configuration for Railway deployment - MINIMAL VERSION
"""
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Railway Django is running!'
    })

def api_root(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'Parcial 1 Backend - Railway',
        'endpoints': ['/api/test/health/', '/admin/']
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/test/health/', health_check, name='health-check'),
    path('', api_root, name='root'),
]