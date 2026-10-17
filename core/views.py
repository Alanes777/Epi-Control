from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Colaborador, EPI, Emprestimo
from .forms import ColaboradorForm


def home(request):
    """
    Página 1 — Página Inicial do EPI Control.
    Apresenta a visão geral do sistema, objetivo e links rápidos de navegação.
    """
    total_colaboradores = Colaborador.objects.count()
    total_epis = EPI.objects.count()
    total_emprestimos = Emprestimo.objects.count()

    context = {
        'total_colaboradores': total_colaboradores,
        'total_epis': total_epis,
        'total_emprestimos': total_emprestimos,
    }
    return render(request, 'home.html', context)


def colaborador_list(request):
    """
    Página 3 — Pesquisa e Listagem de Colaboradores.
    Lista colaboradores em tabela com busca pelo nome (completo ou parcial).
    """
    termo_busca = request.GET.get('q', '').strip()

    if termo_busca:
        # Pesquisa persistida no banco de dados por parte do nome
        colaboradores = Colaborador.objects.filter(nome__icontains=termo_busca)
    else:
        colaboradores = Colaborador.objects.all()

    context = {
        'colaboradores': colaboradores,
        'termo_busca': termo_busca,
        'total_encontrados': colaboradores.count(),
    }
    return render(request, 'colaboradores/colaborador_list.html', context)


def colaborador_create(request):
    """
    Página 2 — Cadastro de Colaboradores.
    Processa o formulário de cadastro, valida os dados e, após o envio com sucesso,
    permanece na página de cadastro permitindo cadastrar outros colaboradores.
    """
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            colaborador = form.save()
            messages.success(
                request,
                f"Colaborador '{colaborador.nome}' (Matrícula: {colaborador.matricula}) cadastrado com sucesso!"
            )
            # Permanece na página de cadastro com formulário limpo para cadastrar outro
            return redirect('colaborador_create')
        else:
            messages.error(
                request,
                "Não foi possível cadastrar o colaborador. Por favor, verifique os erros destacados abaixo."
            )
    else:
        form = ColaboradorForm()

    context = {
        'form': form,
        'titulo_pagina': 'Cadastrar Novo Colaborador',
        'is_edicao': False,
    }
    return render(request, 'colaboradores/colaborador_form.html', context)


def colaborador_update(request, pk):
    """
    Página 4 — Edição de Colaboradores.
    Carrega os dados existentes do colaborador, valida e persiste as alterações no banco.
    """
    colaborador = get_object_or_404(Colaborador, pk=pk)

    if request.method == 'POST':
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Dados do colaborador '{colaborador.nome}' atualizados com sucesso!"
            )
            return redirect('colaborador_list')
        else:
            messages.error(
                request,
                "Não foi possível salvar as alterações. Corrija os erros destacados no formulário."
            )
    else:
        form = ColaboradorForm(instance=colaborador)

    context = {
        'form': form,
        'colaborador': colaborador,
        'titulo_pagina': f'Editar Colaborador: {colaborador.nome}',
        'is_edicao': True,
    }
    return render(request, 'colaboradores/colaborador_form.html', context)


@require_POST
def colaborador_delete(request, pk):
    """
    Exclusão de Colaboradores.
    Atende ao requisito: protegida por requisição POST com CSRF. Não aceita GET.
    """
    colaborador = get_object_or_404(Colaborador, pk=pk)
    nome = colaborador.nome
    matricula = colaborador.matricula

    try:
        colaborador.delete()
        messages.success(
            request,
            f"Colaborador '{nome}' (Matrícula: {matricula}) foi excluído com sucesso!"
        )
    except Exception as e:
        messages.error(
            request,
            f"Erro ao excluir o colaborador '{nome}': {str(e)}"
        )

    return redirect('colaborador_list')


def equipamentos_view(request):
    """
    Módulo de Equipamentos (EPIs): página informativa indicando desenvolvimento futuro (RF06).
    """
    context = {
        'modulo': 'Equipamentos de Proteção Individual (EPIs)',
        'descricao': 'Módulo para controle de estoque, catalogação de EPIs e gestão de Certificados de Aprovação (C.A.).',
        'requisito': 'RF06',
    }
    return render(request, 'em_desenvolvimento.html', context)


def emprestimos_view(request):
    """
    Módulo de Empréstimos: página informativa indicando desenvolvimento futuro (RF07, RF08, RF09).
    """
    context = {
        'modulo': 'Empréstimos e Devoluções de EPIs',
        'descricao': 'Módulo para registro de retiradas, cautelas, prazos de devolução e histórico de EPIs por colaborador.',
        'requisito': 'RF07, RF08 e RF09',
    }
    return render(request, 'em_desenvolvimento.html', context)
