"""
Servicio para el envío de emails del sistema
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio centralizado para el envío de emails"""
    
    @staticmethod
    def _get_base_context() -> Dict:
        """Contexto base para todos los emails"""
        return {
            'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
            'admin_panel_url': getattr(settings, 'ADMIN_PANEL_URL', 'http://localhost:8000/admin'),
        }
    
    @staticmethod
    def _send_html_email(
        template_name: str, 
        context: Dict, 
        subject: str, 
        recipient_list: List[str],
        from_email: Optional[str] = None
    ) -> bool:
        """Envía un email HTML usando template"""
        try:
            # Agregar contexto base
            full_context = {**EmailService._get_base_context(), **context}
            
            # Renderizar template HTML
            html_message = render_to_string(template_name, full_context)
            
            # Crear versión texto plano
            plain_message = strip_tags(html_message)
            
            # Configurar from_email
            if not from_email:
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@condominio.com')
            
            # Enviar email
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False
            )
            
            # logger.info(f"Email enviado exitosamente: {subject} -> {recipient_list}")
            return True
            
        except Exception as e:
            # logger.error(f"Error enviando email: {e}")
            return False
    
    @staticmethod
    def enviar_nueva_solicitud_admin(solicitud, familiares_count: int = 0) -> bool:
        """
        NOTA: Esta función está deshabilitada por diseño.
        Los administradores NO reciben emails de notificación.
        Solo gestionan las solicitudes desde su panel administrativo.
        """
    # logger.info(f"Solicitud creada: {solicitud.nombres} {solicitud.apellidos} - Token: {solicitud.token_seguimiento}")
    # logger.info("Los administradores pueden revisar esta solicitud desde el panel administrativo")
        return True
    
    @staticmethod
    def enviar_confirmacion_solicitud(solicitud, familiares_count: int = 0) -> bool:
        """Envía confirmación de solicitud al solicitante"""
        context = {
            'solicitud': solicitud,
            'familiares_count': familiares_count,
        }
        
        return EmailService._send_html_email(
            template_name='emails/confirmacion_solicitud.html',
            context=context,
            subject='✅ Solicitud Recibida - Sistema Condominio',
            recipient_list=[solicitud.email]
        )
    
    @staticmethod
    def enviar_solicitud_aprobada(solicitud, usuario_creado) -> bool:
        """Notifica aprobación de solicitud"""
        context = {
            'solicitud': solicitud,
            'usuario_creado': usuario_creado,
        }
        
        return EmailService._send_html_email(
            template_name='emails/solicitud_aprobada.html',
            context=context,
            subject='🎉 Solicitud Aprobada - Bienvenido al Sistema',
            recipient_list=[solicitud.email]
        )
    
    @staticmethod
    def enviar_solicitud_rechazada(solicitud) -> bool:
        """Notifica rechazo de solicitud"""
        context = {
            'solicitud': solicitud,
        }
        
        return EmailService._send_html_email(
            template_name='emails/solicitud_rechazada.html',
            context=context,
            subject='❌ Solicitud Rechazada - Sistema Condominio',
            recipient_list=[solicitud.email]
        )
    
    @staticmethod
    def test_email_configuration() -> Dict[str, bool]:
        """Prueba la configuración de email enviando un email de prueba"""
        test_results = {
            'configuration_ok': False,
            'send_test_ok': False,
        }
        
        try:
            # Verificar configuración básica
            backend = getattr(settings, 'EMAIL_BACKEND', None)
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
            
            if backend and from_email:
                test_results['configuration_ok'] = True
            
            # Intentar enviar email de prueba (solo si está configurado)
            if test_results['configuration_ok']:
                test_email = EmailService._send_html_email(
                    template_name='emails/base.html',
                    context={'message': 'Email de prueba del sistema'},
                    subject='🧪 Prueba de Configuración de Email',
                    recipient_list=['test@example.com']  # Email de prueba
                )
                test_results['send_test_ok'] = test_email
                
        except Exception as e:
            # logger.error(f"Error en prueba de email: {e}")
            pass
        return test_results