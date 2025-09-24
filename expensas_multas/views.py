from rest_framework import viewsets
from core.models import ExpensasMensuales
from .serializers import ExpensasMensualesSerializer

class ExpensasMensualesViewSet(viewsets.ModelViewSet):
    """
    Este ViewSet gestiona las operaciones CRUD para las expensas mensuales.
    """
    queryset = ExpensasMensuales.objects.all()
    serializer_class = ExpensasMensualesSerializer
