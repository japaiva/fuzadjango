from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    NIVEL_CHOICES = [
        ('admin', 'Admin'),
        ('engenharia', 'Engenharia'),
        ('vendedor', 'Vendedor'),
    ]
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)

    class Meta:
        db_table = 'usuarios'

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