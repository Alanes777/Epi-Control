from django.urls import path
from . import views

urlpatterns = [
    # Página Inicial
    path('', views.home, name='home'),

    # Módulo de Colaboradores
    path('colaboradores/', views.colaborador_list, name='colaborador_list'),
    path('colaboradores/novo/', views.colaborador_create, name='colaborador_create'),
    path('colaboradores/<int:pk>/editar/', views.colaborador_update, name='colaborador_update'),
    path('colaboradores/<int:pk>/excluir/', views.colaborador_delete, name='colaborador_delete'),

    # Módulo de Equipamentos (EPIs)
    path('equipamentos/', views.epi_list, name='epi_list'),
    path('equipamentos/novo/', views.epi_create, name='epi_create'),
    path('equipamentos/<int:pk>/editar/', views.epi_update, name='epi_update'),
    path('equipamentos/<int:pk>/excluir/', views.epi_delete, name='epi_delete'),

    # Módulo de Controle de EPI (Empréstimos e Devoluções)
    path('emprestimos/', views.emprestimo_list, name='emprestimo_list'),
    path('emprestimos/novo/', views.emprestimo_create, name='emprestimo_create'),
    path('emprestimos/<int:pk>/editar/', views.emprestimo_update, name='emprestimo_update'),
    path('emprestimos/<int:pk>/excluir/', views.emprestimo_delete, name='emprestimo_delete'),
]
