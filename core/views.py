from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone
from .models import Colaborador, EPI, Emprestimo, ItemEmprestimo
from .forms import ColaboradorForm, EPIForm, EmprestimoForm, DevolucaoForm


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
# MÓDULO DE EMPRÉSTIMOS E DEVOLUÇÕES (RF07 E RF09)
# ========================================================

def emprestimo_list(request):
    """
    Página de Listagem e Consulta de Empréstimos de EPIs (RF07 e RF09).
    Permite filtrar por colaborador, status e período (data inicial e final).
    """
    colaborador_id = request.GET.get('colaborador', '').strip()
    status_filtro = request.GET.get('status', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()
    termo_busca = request.GET.get('q', '').strip()

    emprestimos = Emprestimo.objects.select_related('colaborador').prefetch_related('itens__epi').all()

    # Filtro por Colaborador selecionado
    if colaborador_id:
        emprestimos = emprestimos.filter(colaborador_id=colaborador_id)

    # Filtro por Busca textual (nome do colaborador ou do EPI)
    if termo_busca:
        emprestimos = emprestimos.filter(
            Q(colaborador__nome__icontains=termo_busca) |
            Q(colaborador__matricula__icontains=termo_busca) |
            Q(itens__epi__nome__icontains=termo_busca)
        ).distinct()

    # Filtro por Status
    if status_filtro:
        emprestimos = emprestimos.filter(status=status_filtro)

    # Filtro por Período (RF07: consultar empréstimos por período)
    if data_inicio:
        emprestimos = emprestimos.filter(data_emprestimo__gte=data_inicio)
    if data_fim:
        emprestimos = emprestimos.filter(data_emprestimo__lte=data_fim)

    # Verifica e atualiza status de atrasados dinamicamente para exibição
    hoje = timezone.now().date()
    for emp in emprestimos:
        if emp.status == 'ATIVO' and emp.data_prevista_devolucao and emp.data_prevista_devolucao < hoje:
            emp.is_atrasado = True
        else:
            emp.is_atrasado = False

    todos_colaboradores = Colaborador.objects.all().order_by('nome')

    context = {
        'emprestimos': emprestimos,
        'todos_colaboradores': todos_colaboradores,
        'colaborador_id': colaborador_id,
        'status_filtro': status_filtro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'termo_busca': termo_busca,
        'total_encontrados': emprestimos.count(),
        'hoje': hoje,
    }
    return render(request, 'emprestimos/emprestimo_list.html', context)


def emprestimo_create(request):
    """
    Registro de Novo Empréstimo / Cautela de EPI (RF09).
    Valida estoque disponível, cria o empréstimo e debita a quantidade do almoxarifado.
    """
    if request.method == 'POST':
        form = EmprestimoForm(request.POST)
        if form.is_valid():
            colaborador = form.cleaned_data['colaborador']
            epi = form.cleaned_data['epi']
            quantidade = form.cleaned_data['quantidade']
            data_emprestimo = form.cleaned_data['data_emprestimo']
            data_prevista_devolucao = form.cleaned_data.get('data_prevista_devolucao')
            observacoes = form.cleaned_data.get('observacoes', '')

            # 1. Cria o Empréstimo
            emprestimo = Emprestimo.objects.create(
                colaborador=colaborador,
                data_emprestimo=data_emprestimo,
                data_prevista_devolucao=data_prevista_devolucao,
                status='ATIVO',
                observacoes=observacoes
            )

            # 2. Cria o Item do Empréstimo
            ItemEmprestimo.objects.create(
                emprestimo=emprestimo,
                epi=epi,
                quantidade=quantidade
            )

            # 3. Baixa no estoque do almoxarifado
            epi.quantidade_estoque -= quantidade
            epi.save()

            messages.success(
                request,
                f"Empréstimo registrado com sucesso! Fornecido(s) {quantidade}x '{epi.nome}' para '{colaborador.nome}'."
            )
            return redirect('emprestimo_list')
        else:
            messages.error(
                request,
                "Não foi possível registrar o empréstimo. Por favor, verifique os erros destacados abaixo."
            )
    else:
        form = EmprestimoForm()

    context = {
        'form': form,
        'titulo_pagina': 'Registrar Novo Empréstimo de EPI',
    }
    return render(request, 'emprestimos/emprestimo_form.html', context)


@require_POST
def emprestimo_devolver(request, pk):
    """
    Registro da Devolução de um Empréstimo de EPI (RF09).
    Atualiza status para 'DEVOLVIDO', data de devolução e reintegra o item ao estoque.
    """
    emprestimo = get_object_or_404(Emprestimo, pk=pk)

    if emprestimo.status == 'DEVOLVIDO':
        messages.warning(request, "Este empréstimo já foi finalizado como devolvido anteriormente.")
        return redirect('emprestimo_list')

    data_devolucao = request.POST.get('data_devolucao')
    retornar_estoque = request.POST.get('retornar_ao_estoque') == 'on'
    obs_devolucao = request.POST.get('observacoes_devolucao', '').strip()

    try:
        data_efetiva = datetime.strptime(data_devolucao, '%Y-%m-%d').date() if data_devolucao else timezone.now().date()
    except ValueError:
        data_efetiva = timezone.now().date()

    # Atualiza o Empréstimo
    emprestimo.status = 'DEVOLVIDO'
    emprestimo.data_devolucao = data_efetiva
    if obs_devolucao:
        obs_atual = emprestimo.observacoes or ""
        emprestimo.observacoes = f"{obs_atual}\n[Devolução em {data_efetiva.strftime('%d/%m/%Y')}]: {obs_devolucao}".strip()
    emprestimo.save()

    # Reintegração das peças ao estoque se solicitado
    if retornar_estoque:
        for item in emprestimo.itens.all():
            epi = item.epi
            epi.quantidade_estoque += item.quantidade
            epi.save()

    messages.success(
        request,
        f"Devolução do Empréstimo #{emprestimo.id} (Colaborador: {emprestimo.colaborador.nome}) confirmada com sucesso!"
    )
    return redirect('emprestimo_list')


@require_POST
def emprestimo_delete(request, pk):
    """
    Exclusão de Registro de Empréstimo.
    Protegida por requisição POST com token CSRF.
    """
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    colab_nome = emprestimo.colaborador.nome

    try:
        emprestimo.delete()
        messages.success(
            request,
            f"Registro de empréstimo do colaborador '{colab_nome}' excluído com sucesso!"
        )
    except Exception as e:
        messages.error(
            request,
            f"Erro ao excluir o empréstimo: {str(e)}"
        )

    return redirect('emprestimo_list')

