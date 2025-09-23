from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nombre

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombres, apellidos, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo email es obligatorio')
        if not nombres:
            raise ValueError('El campo nombres es obligatorio')
        if not apellidos:
            raise ValueError('El campo apellidos es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            nombres=nombres,
            apellidos=apellidos,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombres, apellidos, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('estado', 'ACTIVO')
        return self.create_user(email, nombres, apellidos, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    ESTADOS = (("ACTIVO","ACTIVO"),("INACTIVO","INACTIVO"),("BLOQUEADO","BLOQUEADO"))
    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, unique=True)
    telefono = models.CharField(max_length=25, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=1, choices=(('M','Masculino'),('F','Femenino')), blank=True, null=True)
    documento_identidad = models.CharField(max_length=30, blank=True, null=True)
    pais = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="ACTIVO")
    roles = models.ManyToManyField(Rol, related_name="usuarios", blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Evitar conflictos con el modelo User de Django
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='authz_usuarios',  # Cambiar related_name
        help_text='Los grupos a los que pertenece este usuario.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='authz_usuarios',  # Cambiar related_name
        help_text='Permisos específicos para este usuario.',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombres', 'apellidos']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nombres} {self.apellidos} <{self.email}>"
