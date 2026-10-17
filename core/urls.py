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
    
    # Módulo de Equipamentos (EPIs - CRUD completo - RF06)
    path('equipamentos/', views.epi_list, name='epi_list'),
    path('equipamentos/novo/', views.epi_create, name='epi_create'),
    path('equipamentos/<int:pk>/editar/', views.epi_update, name='epi_update'),
    path('equipamentos/<int:pk>/excluir/', views.epi_delete, name='epi_delete'),
    
    # Módulo de Empréstimos e Devoluções (CRUD completo - RF07 e RF09)
    path('emprestimos/', views.emprestimo_list, name='emprestimo_list'),
    path('emprestimos/novo/', views.emprestimo_create, name='emprestimo_create'),
    path('emprestimos/<int:pk>/devolver/', views.emprestimo_devolver, name='emprestimo_devolver'),
    path('emprestimos/<int:pk>/excluir/', views.emprestimo_delete, name='emprestimo_delete'),
]
