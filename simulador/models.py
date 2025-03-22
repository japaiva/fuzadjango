from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Custo(models.Model):
    codigo = models.CharField(max_length=4, primary_key=True)
    descricao = models.CharField(max_length=50)
    unidade = models.CharField(max_length=10)
    valor = models.FloatField()

    class Meta:
        db_table = 'custos'

class Parametro(models.Model):
    parametro = models.CharField(max_length=50)
    valor = models.FloatField()

    class Meta:
        db_table = 'parametros'

class Usuario(AbstractUser):
    NIVEL_CHOICES = [
        ('admin', 'Admin'),
        ('engenharia', 'Engenharia'),
        ('vendedor', 'Vendedor'),
    ]

    # Desabilitar relacionamentos explicitamente
    groups = None  # Remove o relacionamento com grupos
    user_permissions = None  # Remove o relacionamento com permissões individuais
    
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    # Removi o last_login duplicado
    is_superuser = models.BooleanField(default=False)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'usuarios'