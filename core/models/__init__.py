# Este archivo importa los modelos de cada módulo
from .propiedades_residentes import *
from .seguridad_ia import *
from .administracion import *

# Importar modelos centralizados desde authz para compatibilidad
from authz.models import (
    Persona, 
    RelacionesPropietarioInquilino, 
    FamiliarPropietario as FamiliarResidente  # Alias para compatibilidad
)