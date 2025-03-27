from django.urls import path
from . import views

app_name = 'simulador' 

urlpatterns = [
    path('', views.home, name='home'),
    path('cliente/', views.cliente, name='cliente'),
    path('elevador/', views.elevador, name='elevador'),
    path('portas/', views.portas, name='portas'),
    path('cabine/', views.cabine, name='cabine'),
    path('resumo/', views.resumo, name='resumo'),
    path('logout/', views.logout_view, name='logout'), 
    path('reiniciar/', views.reiniciar_simulacao, name='reiniciar_simulacao'),

    path('atualizar-preco-final/', views.atualizar_preco_final, name='atualizar_preco_final'),

    # Novas URLs para PDFs
    path('gerar-pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('proposta-comercial/', views.proposta_comercial, name='proposta_comercial'),
    
    # URLs de autenticação
    path('logout/', views.logout_view, name='logout'),

    # URLs para Usuários
    path('usuarios/', views.usuario_list, name='usuario_list'),
    path('usuarios/create/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/update/', views.usuario_update, name='usuario_update'),
    path('usuarios/<int:pk>/delete/', views.usuario_delete, name='usuario_delete'),
    
    # URLs para Custos
    path('custos/', views.custo_list, name='custo_list'),
    path('custos/create/', views.custo_create, name='custo_create'),
    path('custos/<str:pk>/update/', views.custo_update, name='custo_update'),
    path('custos/<str:pk>/delete/', views.custo_delete, name='custo_delete'),
    
    path('parametros/', views.parametro_list, name='parametro_list'),
    path('parametros/create/', views.parametro_create, name='parametro_create'),
    path('parametros/<int:pk>/update/', views.parametro_update, name='parametro_update'),
    path('parametros/<int:pk>/delete/', views.parametro_delete, name='parametro_delete'),

]