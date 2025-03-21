from django.urls import path
from . import views

app_name = 'simulador'  # 🔥 Isso registra o namespace!


urlpatterns = [
    path('', views.home, name='home'),
    path('cliente/', views.cliente, name='cliente'),
    path('elevador/', views.elevador, name='elevador'),
    path('portas/', views.portas, name='portas'),
    path('cabine/', views.cabine, name='cabine'),
    path('resumo/', views.resumo, name='resumo'),
    path('reiniciar/', views.reiniciar_simulacao, name='reiniciar_simulacao'),
]