
from django.test import TestCase
from django.contrib.auth import get_user_model
from authz.models import SolicitudRegistroPropietario
from core.models.administracion import BitacoraAcciones

class BitacoraSignalsTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')

    def test_bitacora_signal_solicitud(self):
        # Crear
        solicitud = SolicitudRegistroPropietario.objects.create(
            nombres='Juan',
            apellidos='Pérez',
            documento_identidad='12345678',
            fecha_nacimiento='1990-01-01',
            email='juan@example.com',
            telefono='5551234',
            numero_casa='A-101',
            estado='PENDIENTE',
            usuario_creado=self.user
        )
        bitacora = BitacoraAcciones.objects.filter(tabla_afectada='SolicitudRegistroPropietario', registro_id=solicitud.id)
        self.assertTrue(bitacora.exists())
        # Actualizar
        solicitud.estado = 'APROBADA'
        solicitud.save()
        bitacora_update = BitacoraAcciones.objects.filter(tabla_afectada='SolicitudRegistroPropietario', registro_id=solicitud.id, accion_tipo='UPDATE')
        self.assertTrue(bitacora_update.exists())
        # Eliminar
        solicitud_id = solicitud.id
        solicitud.delete()
        bitacora_delete = BitacoraAcciones.objects.filter(tabla_afectada='SolicitudRegistroPropietario', registro_id=solicitud_id, accion_tipo='DELETE')
        self.assertTrue(bitacora_delete.exists())

    def test_bitacora_signal_relacion_inquilino(self):
        from authz.models import RelacionesPropietarioInquilino
        propietario = self.user
        inquilino = self.user
        relacion = RelacionesPropietarioInquilino.objects.create(propietario=propietario, inquilino=inquilino, vivienda_id=1)
        bitacora = BitacoraAcciones.objects.filter(tabla_afectada='RelacionesPropietarioInquilino', registro_id=relacion.id)
        self.assertTrue(bitacora.exists())
        relacion.delete()
        bitacora_delete = BitacoraAcciones.objects.filter(tabla_afectada='RelacionesPropietarioInquilino', registro_id=relacion.id, accion_tipo='DELETE')
        self.assertTrue(bitacora_delete.exists())

    def test_bitacora_signal_familiar(self):
        from authz.models import FamiliarPropietario, Persona
        propietario = self.user
        persona = Persona.objects.create(nombre='Fam', apellido='Test', documento_identidad='777', email='fam@example.com')
        familiar = FamiliarPropietario.objects.create(propietario=propietario, persona=persona, parentesco='hijo')
        bitacora = BitacoraAcciones.objects.filter(tabla_afectada='FamiliarPropietario', registro_id=familiar.id)
        self.assertTrue(bitacora.exists())
        familiar.delete()
        bitacora_delete = BitacoraAcciones.objects.filter(tabla_afectada='FamiliarPropietario', registro_id=familiar.id, accion_tipo='DELETE')
        self.assertTrue(bitacora_delete.exists())

    def test_bitacora_signal_visita(self):
        from core.models.propiedades_residentes import Visita, Persona
        persona_autorizante = Persona.objects.create(nombre='Aut', apellido='Test', documento_identidad='666', email='aut@example.com')
        visita = Visita.objects.create(persona_autorizante=persona_autorizante, nombre_visitante='Visitante', estado='programada')
        bitacora = BitacoraAcciones.objects.filter(tabla_afectada='Visita', registro_id=visita.id)
        self.assertTrue(bitacora.exists())
        visita.delete()
        bitacora_delete = BitacoraAcciones.objects.filter(tabla_afectada='Visita', registro_id=visita.id, accion_tipo='DELETE')
        self.assertTrue(bitacora_delete.exists())

    def test_visualizar_bitacora(self):
        from core.models.administracion import BitacoraAcciones
        registros = BitacoraAcciones.objects.all()
        print("\n--- Registros en Bitácora ---")
        for registro in registros:
            print(f"{registro.fecha_hora} | {registro.tabla_afectada} | {registro.accion_tipo} | {registro.registro_id} | {registro.descripcion}")
        self.assertTrue(registros.exists())
