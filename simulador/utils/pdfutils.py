from django.urls import path
from . import views

app_name = 'simulador'

urlpatterns = [
    # URLs existentes
    path('', views.home, name='home'),
    path('inicio/', views.inicio, name='inicio'),
    path('cliente/', views.cliente, name='cliente'),
    path('elevador/', views.elevador, name='elevador'),
    path('portas/', views.portas, name='portas'),
    path('cabine/', views.cabine, name='cabine'),
    path('resumo/', views.resumo, name='resumo'),
    path('reiniciar/', views.reiniciar_simulacao, name='reiniciar_simulacao'),
    
    # Novas URLs para PDFs
    path('gerar-pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('proposta-comercial/', views.proposta_comercial, name='proposta_comercial'),
    
    # URLs de autenticação
    path('logout/', views.logout_view, name='logout'),
    
    # URLs CRUD
    path('usuarios/', views.usuario_list, name='usuario_list'),
    path('usuarios/novo/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.usuario_update, name='usuario_update'),
    path('usuarios/<int:pk>/excluir/', views.usuario_delete, name='usuario_delete'),
    
    path('custos/', views.custo_list, name='custo_list'),
    path('custos/novo/', views.custo_create, name='custo_create'),
    path('custos/<int:pk>/editar/', views.custo_update, name='custo_update'),
    path('custos/<int:pk>/excluir/', views.custo_delete, name='custo_delete'),
    
    path('parametros/', views.parametro_list, name='parametro_list'),
    path('parametros/novo/', views.parametro_create, name='parametro_create'),
    path('parametros/<int:pk>/editar/', views.parametro_update, name='parametro_update'),
    path('parametros/<int:pk>/excluir/', views.parametro_delete, name='parametro_delete'),
]