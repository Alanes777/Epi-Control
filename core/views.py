from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone
from .models import Colaborador, EPI, Emprestimo, ItemEmprestimo
from .forms import ColaboradorForm, EPIForm, EmprestimoCreateForm, EmprestimoUpdateForm


def home(request):
    """
    Página Inicial do EPI Control (Construção Civil).
    Apresenta a visão geral do sistema, objetivos de segurança do trabalho e estatísticas.
    """
    total_colaboradores = Colaborador.objects.count()
    total_epis = EPI.objects.count()
    total_emprestimos = Emprestimo.objects.count()
    emprestimos_ativos = Emprestimo.objects.filter(status='EMPRESTADO').count()

    context = {
        'total_colaboradores': total_colaboradores,
        'total_epis': total_epis,
        'total_emprestimos': total_emprestimos,
        'emprestimos_ativos': emprestimos_ativos,
    }
    return render(request, 'home.html', context)


# ========================================================
# MÓDULO DE COLABORADORES (CRUD COMPLETO)
# ========================================================

def colaborador_list(request):
    """
    Pesquisa e Listagem de Colaboradores.
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
    Cadastro de Colaboradores.
    Ao cadastrar, exibe mensagem de sucesso ou falha.
    Após o cadastro com sucesso, o sistema permanece na tela de cadastro.
    """
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            colaborador = form.save()
            messages.success(
                request,
                f"Colaborador '{colaborador.nome}' (Matrícula: {colaborador.matricula}) cadastrado com sucesso!"
            )
            # Permanece na página de cadastro permitindo novos cadastros
            return redirect('colaborador_create')
        else:
            messages.error(
                request,
                "Falha ao cadastrar colaborador. Por favor, verifique os erros destacados abaixo."
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
    Edição de Colaboradores.
    Carrega os dados existentes do colaborador e persiste as alterações.
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
                "Falha ao salvar as alterações do colaborador. Corrija os erros destacados."
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
    Protegida por requisição POST com CSRF. Não aceita GET.
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
# MÓDULO DE EQUIPAMENTOS (EPIs)
# ========================================================

def epi_list(request):
    """
    Pesquisa e Listagem de Equipamentos de Proteção Individual.
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
    Cadastro de Equipamentos de Proteção Individual.
    Exibe mensagem de sucesso ou falha no momento da criação.
    Após o cadastro, o sistema permanece na tela de cadastro.
    """
    if request.method == 'POST':
        form = EPIForm(request.POST)
        if form.is_valid():
            epi = form.save()
            ca = f" (C.A. {epi.certificado_aprovacao})" if epi.certificado_aprovacao else ""
            messages.success(
                request,
                f"Equipamento '{epi.nome}'{ca} cadastrado com sucesso no almoxarifado!"
            )
            # Permanece na tela de cadastro permitindo novos registros
            return redirect('epi_create')
        else:
            messages.error(
                request,
                "Falha ao cadastrar equipamento. Verifique os campos destacados abaixo."
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
    Edição de Equipamentos de Proteção Individual.
    Exibe tela parecida com a de cadastro carregando as informações para atualização.
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
                "Falha ao atualizar o equipamento. Corrija os erros destacados no formulário."
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
            f"Equipamento '{nome}' foi excluído com sucesso do almoxarifado!"
        )
    except Exception as e:
        messages.error(
            request,
            f"Erro ao excluir o equipamento '{nome}': {str(e)}"
        )

    return redirect('epi_list')


# ========================================================
# MÓDULO DE CONTROLE DE EPI (EMPRÉSTIMOS E DEVOLUÇÕES)
# ========================================================

def emprestimo_list(request):
    """
    Pesquisa e Listagem de Empréstimos de EPIs com Filtro AND.
    Permite filtrar simultaneamente por:
    - Nome do colaborador (AND)
    - Nome do equipamento (AND)
    - Status do empréstimo (AND)
    Exemplo: Se pesquisar pelo nome do colaborador + status 'EMPRESTADO',
    é possível ver exatamente quais equipamentos o colaborador retirou e ainda não devolveu.
    """
    colaborador_nome = request.GET.get('colaborador_nome', '').strip()
    epi_nome = request.GET.get('epi_nome', '').strip()
    status_filtro = request.GET.get('status', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()

    # Query inicial otimizada
    emprestimos = Emprestimo.objects.select_related('colaborador', 'epi').prefetch_related('itens__epi').all()

    # Aplicação de Filtros do tipo AND
    if colaborador_nome:
        emprestimos = emprestimos.filter(
            Q(colaborador__nome__icontains=colaborador_nome) |
            Q(colaborador__matricula__icontains=colaborador_nome)
        )

    if epi_nome:
        emprestimos = emprestimos.filter(
            Q(epi__nome__icontains=epi_nome) |
            Q(itens__epi__nome__icontains=epi_nome)
        ).distinct()

    if status_filtro:
        emprestimos = emprestimos.filter(status=status_filtro)

    if data_inicio:
        emprestimos = emprestimos.filter(data_emprestimo__gte=data_inicio)

    if data_fim:
        emprestimos = emprestimos.filter(data_emprestimo__lte=data_fim)

    # Identificação de atraso para status 'Emprestado'
    hoje = timezone.now().date()
    for emp in emprestimos:
        if emp.status == 'EMPRESTADO' and emp.data_prevista_devolucao and emp.data_prevista_devolucao < hoje:
            emp.is_atrasado = True
        else:
            emp.is_atrasado = False

    context = {
        'emprestimos': emprestimos,
        'colaborador_nome': colaborador_nome,
        'epi_nome': epi_nome,
        'status_filtro': status_filtro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_encontrados': emprestimos.count(),
        'hoje': hoje,
    }
    return render(request, 'emprestimos/emprestimo_list.html', context)


def relatorio_list(request):
    """
    Tela de Relatórios de Controle de EPIs (Requisito Específico).
    Permite pesquisar pelo nome do colaborador, nome do equipamento e status,
    aplicando filtro do tipo AND.
    Exemplo: Pesquisar por colaborador + status 'EMPRESTADO' para auditar exatamente quais EPIs
    o colaborador retirou e ainda não devolveu.
    """
    colaborador_nome = request.GET.get('colaborador_nome', '').strip()
    epi_nome = request.GET.get('epi_nome', '').strip()
    status_filtro = request.GET.get('status', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()

    # Query inicial otimizada
    emprestimos = Emprestimo.objects.select_related('colaborador', 'epi').prefetch_related('itens__epi').all()

    # Aplicação do Filtro do tipo AND
    if colaborador_nome:
        emprestimos = emprestimos.filter(
            Q(colaborador__nome__icontains=colaborador_nome) |
            Q(colaborador__matricula__icontains=colaborador_nome)
        )

    if epi_nome:
        emprestimos = emprestimos.filter(
            Q(epi__nome__icontains=epi_nome) |
            Q(itens__epi__nome__icontains=epi_nome)
        ).distinct()

    if status_filtro:
        emprestimos = emprestimos.filter(status=status_filtro)

    if data_inicio:
        emprestimos = emprestimos.filter(data_emprestimo__gte=data_inicio)

    if data_fim:
        emprestimos = emprestimos.filter(data_emprestimo__lte=data_fim)

    # Identificação de atraso para status 'Emprestado'
    hoje = timezone.now().date()
    for emp in emprestimos:
        if emp.status == 'EMPRESTADO' and emp.data_prevista_devolucao and emp.data_prevista_devolucao < hoje:
            emp.is_atrasado = True
        else:
            emp.is_atrasado = False

    # Estatísticas agregadas do relatório
    total_encontrados = emprestimos.count()
    total_emprestados = emprestimos.filter(status='EMPRESTADO').count()
    total_fornecidos = emprestimos.filter(status='FORNECIDO').count()
    total_devolvidos = emprestimos.filter(status='DEVOLVIDO').count()
    total_danificados = emprestimos.filter(status='DANIFICADO').count()
    total_perdidos = emprestimos.filter(status='PERDIDO').count()

    context = {
        'emprestimos': emprestimos,
        'colaborador_nome': colaborador_nome,
        'epi_nome': epi_nome,
        'status_filtro': status_filtro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_encontrados': total_encontrados,
        'total_emprestados': total_emprestados,
        'total_fornecidos': total_fornecidos,
        'total_devolvidos': total_devolvidos,
        'total_danificados': total_danificados,
        'total_perdidos': total_perdidos,
        'hoje': hoje,
    }
    return render(request, 'relatorios/relatorio_list.html', context)


def emprestimo_create(request):
    """
    Cadastro / Registro de Novo Empréstimo de EPI.
    - Status permitidos apenas 'Emprestado' e 'Fornecido' (ocultando Devolvido, Danificado, Perdido).
    - Data prevista deve ser posterior à data atual (para Emprestado).
    - Valida estoque e debita do almoxarifado.
    - Exibe mensagem de sucesso ou falha no momento do cadastro.
    - Após o cadastro, permanece na tela de cadastro.
    """
    if request.method == 'POST':
        form = EmprestimoCreateForm(request.POST)
        if form.is_valid():
            colaborador = form.cleaned_data['colaborador']
            epi = form.cleaned_data['epi']
            quantidade = form.cleaned_data['quantidade']
            data_emprestimo = form.cleaned_data['data_emprestimo']
            data_prevista_devolucao = form.cleaned_data.get('data_prevista_devolucao')
            status = form.cleaned_data['status']
            observacoes = form.cleaned_data.get('observacoes', '')

            # 1. Criação do Empréstimo com chaves estrangeiras adequadas
            emprestimo = Emprestimo.objects.create(
                colaborador=colaborador,
                epi=epi,
                quantidade=quantidade,
                data_emprestimo=data_emprestimo,
                data_prevista_devolucao=data_prevista_devolucao,
                status=status,
                observacoes=observacoes
            )

            # 2. Criação do ItemEmprestimo associado
            ItemEmprestimo.objects.create(
                emprestimo=emprestimo,
                epi=epi,
                quantidade=quantidade
            )

            # 3. Baixa no estoque físico
            epi.quantidade_estoque -= quantidade
            epi.save()

            messages.success(
                request,
                f"Empréstimo registrado com sucesso! Fornecido(s) {quantidade}x '{epi.nome}' para o colaborador '{colaborador.nome}'."
            )
            # Permanece na tela de cadastro para novos registros
            return redirect('emprestimo_create')
        else:
            messages.error(
                request,
                "Falha ao registrar o empréstimo. Por favor, verifique os erros destacados abaixo."
            )
    else:
        form = EmprestimoCreateForm()

    context = {
        'form': form,
        'titulo_pagina': 'Registrar Novo Empréstimo de EPI',
    }
    return render(request, 'emprestimos/emprestimo_form.html', context)


def emprestimo_update(request, pk):
    """
    Atualização de Status do Empréstimo de EPI.
    Requisitos:
    - Exibe tela parecida com a de cadastro.
    - Impede a alteração de: Colaborador, Equipamento, Data do Empréstimo e Data Prevista.
    - Permite alterar: Status (todos os 5 status), Data de Devolução e Observação na Devolução.
    - Campos de devolução são exibidos apenas quando selecionados Devolvido, Danificado ou Perdido.
    """
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    status_anterior = emprestimo.status

    if request.method == 'POST':
        form = EmprestimoUpdateForm(request.POST, instance=emprestimo)
        if form.is_valid():
            novo_status = form.cleaned_data['status']
            retornar_estoque = form.cleaned_data.get('retornar_ao_estoque')
            emprestimo_salvo = form.save()

            # Se o item foi Devolvido e marcado para retornar ao estoque, reincorpora a quantidade ao almoxarifado
            if status_anterior in ['EMPRESTADO', 'FORNECIDO'] and novo_status == 'DEVOLVIDO' and retornar_estoque:
                if emprestimo_salvo.epi:
                    emprestimo_salvo.epi.quantidade_estoque += emprestimo_salvo.quantidade
                    emprestimo_salvo.epi.save()

            messages.success(
                request,
                f"Status do empréstimo #{emprestimo.id} atualizado com sucesso para '{emprestimo_salvo.get_status_display()}'!"
            )
            return redirect('emprestimo_list')
        else:
            messages.error(
                request,
                "Falha ao atualizar o status do empréstimo. Verifique os campos destacados."
            )
    else:
        form = EmprestimoUpdateForm(instance=emprestimo)

    context = {
        'form': form,
        'emprestimo': emprestimo,
        'titulo_pagina': f'Atualizar Status — Cautela #{emprestimo.id}',
    }
    return render(request, 'emprestimos/emprestimo_edit.html', context)


@require_POST
def emprestimo_delete(request, pk):
    """
    Exclusão de Registro de Empréstimo.
    Protegida por requisição POST com token CSRF.
    """
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    colab_nome = emprestimo.colaborador.nome
    item_nome = emprestimo.epi.nome if emprestimo.epi else "EPI"

    try:
        emprestimo.delete()
        messages.success(
            request,
            f"Registro de empréstimo ({item_nome} para '{colab_nome}') excluído com sucesso!"
        )
    except Exception as e:
        messages.error(
            request,
            f"Erro ao excluir o empréstimo: {str(e)}"
        )

    return redirect('emprestimo_list')
