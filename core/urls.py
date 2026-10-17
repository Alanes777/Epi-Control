from django.urls import path
from . import views

urlpatterns = [
    # Página 1 — Página Inicial
    path('', views.home, name='home'),
    
    # Módulo de Colaboradores (CRUD completo - RF01 a RF05)
    path('colaboradores/', views.colaborador_list, name='colaborador_list'),
    path('colaboradores/novo/', views.colaborador_create, name='colaborador_create'),
    path('colaboradores/<int:pk>/editar/', views.colaborador_update, name='colaborador_update'),
    path('colaboradores/<int:pk>/excluir/', views.colaborador_delete, name='colaborador_delete'),
    
    # Módulos em desenvolvimento
    path('equipamentos/', views.equipamentos_view, name='equipamentos'),
    path('emprestimos/', views.emprestimos_view, name='emprestimos'),
]
