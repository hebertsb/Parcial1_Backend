"""
Endpoint temporal para diagnóstico del problema 405
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET', 'POST'])  # Incluir GET para testing
@permission_classes([IsAuthenticated])
def diagnostico_endpoint(request):
    """
    Endpoint temporal para diagnosticar el problema 405
    """
    print(f"🔍 DIAGNÓSTICO - Método recibido: {request.method}")
    print(f"🔍 DIAGNÓSTICO - Headers: {dict(request.headers)}")
    print(f"🔍 DIAGNÓSTICO - Data: {request.data}")
    
    if request.method == 'GET':
        return Response({
            'status': 'ok',
            'method': 'GET',
            'message': 'Endpoint funcionando correctamente'
        })
    
    elif request.method == 'POST':
        return Response({
            'status': 'ok', 
            'method': 'POST',
            'message': 'POST funcionando correctamente',
            'data_received': request.data
        })
    
    return Response({
        'status': 'error',
        'method': request.method,
        'message': f'Método {request.method} no soportado'
    }, status=status.HTTP_405_METHOD_NOT_ALLOWED)