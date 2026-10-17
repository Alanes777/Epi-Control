from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Colaborador, EPI, Emprestimo
from .forms import ColaboradorForm, EPIForm


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


# ========================================================
# MÓDULO DE COLABORADORES (CRUD COMPLETO - RF01 A RF05)
# ========================================================

def colaborador_list(request):
    """
    Página 3 — Pesquisa e Listagem de Colaboradores.
    Lista colaboradores em tabela com busca pelo nome (completo ou parcial).
    """
    termo_busca = request.GET.get('q', '').strip()

    if termo_busca:
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


# ========================================================
# MÓDULO DE EQUIPAMENTOS (EPIs - RF06)
# ========================================================

def epi_list(request):
    """
    Pesquisa e Listagem de Equipamentos de Proteção Individual (RF06).
    Permite consultar por nome ou número do C.A. no banco de dados.
    """
    termo_busca = request.GET.get('q', '').strip()

    if termo_busca:
        epis = EPI.objects.filter(
            Q(nome__icontains=termo_busca) |
            Q(certificado_aprovacao__icontains=termo_busca) |
            Q(descricao__icontains=termo_busca)
        )
    else:
        epis = EPI.objects.all()

    context = {
        'epis': epis,
        'termo_busca': termo_busca,
        'total_encontrados': epis.count(),
    }
    return render(request, 'equipamentos/epi_list.html', context)


def epi_create(request):
    """
    Cadastro de Equipamentos de Proteção Individual (RF06).
    Após o cadastro, permanece na tela para agilizar múltiplos cadastros no almoxarifado.
    """
    if request.method == 'POST':
        form = EPIForm(request.POST)
        if form.is_valid():
            epi = form.save()
            ca = f" (C.A. {epi.certificado_aprovacao})" if epi.certificado_aprovacao else ""
            messages.success(
                request,
                f"Equipamento '{epi.nome}'{ca} cadastrado com sucesso!"
            )
            return redirect('epi_create')
        else:
            messages.error(
                request,
                "Não foi possível cadastrar o equipamento. Verifique os campos abaixo."
            )
    else:
        form = EPIForm()

    context = {
        'form': form,
        'titulo_pagina': 'Cadastrar Novo Equipamento (EPI)',
        'is_edicao': False,
    }
    return render(request, 'equipamentos/epi_form.html', context)


def epi_update(request, pk):
    """
    Edição de Equipamentos de Proteção Individual (RF06).
    """
    epi = get_object_or_404(EPI, pk=pk)

    if request.method == 'POST':
        form = EPIForm(request.POST, instance=epi)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Equipamento '{epi.nome}' atualizado com sucesso!"
            )
            return redirect('epi_list')
        else:
            messages.error(
                request,
                "Não foi possível salvar as alterações do equipamento. Corrija os erros destacados."
            )
    else:
        form = EPIForm(instance=epi)

    context = {
        'form': form,
        'epi': epi,
        'titulo_pagina': f'Editar Equipamento: {epi.nome}',
        'is_edicao': True,
    }
    return render(request, 'equipamentos/epi_form.html', context)


@require_POST
def epi_delete(request, pk):
    """
    Exclusão de Equipamento (EPI).
    Protegida por requisição POST com token CSRF.
    """
    epi = get_object_or_404(EPI, pk=pk)
    nome = epi.nome

    try:
        epi.delete()
        messages.success(
            request,
            f"Equipamento '{nome}' foi excluído com sucesso!"
        )
    except Exception as e:
        messages.error(
            request,
            f"Erro ao excluir o equipamento '{nome}': {str(e)}"
        )

    return redirect('epi_list')


# ========================================================
# MÓDULO DE EMPRÉSTIMOS (EM DESENVOLVIMENTO)
# ========================================================

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
