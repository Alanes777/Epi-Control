from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone
from .models import Setor, Colaborador, EPI, Emprestimo, ItemEmprestimo
from .forms import ColaboradorForm, EPIForm, EmprestimoCreateForm, EmprestimoUpdateForm


# ========================================================
# MÓDULO DE AUTENTICAÇÃO E CONTROLE DE ACESSO
# ========================================================

def user_login(request):
    """
    Tela de Autenticação / Login no EPI Control.
    Permite o acesso ao sistema mediante credenciais válidas.
    Redireciona para a página solicitada previamente (next) ou para a página inicial.
    """
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next') or request.POST.get('next') or 'home'

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            nome_exibicao = user.get_full_name() or user.username
            messages.success(request, f"Seja bem-vindo(a), {nome_exibicao}!")

            # Valida segurança da URL de redirecionamento
            if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(
                request,
                "Usuário ou senha inválidos. Por favor, verifique suas credenciais e tente novamente."
            )
    else:
        form = AuthenticationForm(request)

    context = {
        'form': form,
        'next': next_url,
    }
    return render(request, 'auth/login.html', context)


def user_logout(request):
    """
    Encerra a sessão do usuário atual (Logout) e redireciona para a tela de login.
    """
    if request.user.is_authenticated:
        nome = request.user.get_full_name() or request.user.username
        auth_logout(request)
        messages.info(request, f"Sessão encerrada com sucesso. Até logo, {nome}!")
    return redirect('login')


@login_required
def usuario_list(request):
    """
    Controle de Usuários do Sistema.
    Lista todos os usuários cadastrados, seus perfis/grupos de acesso,
    status de ativação e atalho direto para gestão detalhada no Django Admin.
    """
    termo_busca = request.GET.get('q', '').strip()

    usuarios = User.objects.prefetch_related('groups').all().order_by('username')
    if termo_busca:
        usuarios = usuarios.filter(
            Q(username__icontains=termo_busca) |
            Q(first_name__icontains=termo_busca) |
            Q(last_name__icontains=termo_busca) |
            Q(email__icontains=termo_busca)
        )

    context = {
        'usuarios': usuarios,
        'termo_busca': termo_busca,
        'total_usuarios': usuarios.count(),
        'total_grupos': Group.objects.count(),
    }
    return render(request, 'usuarios/usuario_list.html', context)


# ========================================================
# PÁGINA INICIAL (DASHBOARD)
# ========================================================

@login_required
def home(request):
    """
    Página Inicial do EPI Control (Construção Civil).
    Apresenta a visão geral do sistema, objetivos de segurança do trabalho e estatísticas.
    """
    total_colaboradores = Colaborador.objects.count()
    total_epis = EPI.objects.count()
    total_emprestimos = Emprestimo.objects.count()
    emprestimos_ativos = Emprestimo.objects.filter(status='EMPRESTADO').count()
    total_setores = Setor.objects.count()

    context = {
        'total_colaboradores': total_colaboradores,
        'total_epis': total_epis,
        'total_emprestimos': total_emprestimos,
        'emprestimos_ativos': emprestimos_ativos,
        'total_setores': total_setores,
    }
    return render(request, 'home.html', context)


# ========================================================
# MÓDULO DE COLABORADORES (CRUD COMPLETO)
# ========================================================

@login_required
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


@login_required
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


@login_required
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
@login_required
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

@login_required
def epi_list(request):
    """
    Pesquisa e Listagem de Equipamentos de Proteção Individual.
    Permite localizar EPIs pelo nome ou C.A.
    """
    termo_busca = request.GET.get('q', '').strip()

    if termo_busca:
        epis = EPI.objects.filter(
            Q(nome__icontains=termo_busca) |
            Q(certificado_aprovacao__icontains=termo_busca)
        )
    else:
        epis = EPI.objects.all()

    context = {
        'epis': epis,
        'termo_busca': termo_busca,
        'total_encontrados': epis.count(),
    }
    return render(request, 'equipamentos/epi_list.html', context)


@login_required
def epi_create(request):
    """
    Cadastro de Equipamentos (EPIs).
    Ao cadastrar, exibe mensagem de sucesso ou falha.
    Após o cadastro com sucesso, o sistema permanece na tela de cadastro.
    """
    if request.method == 'POST':
        form = EPIForm(request.POST)
        if form.is_valid():
            epi = form.save()
            messages.success(
                request,
                f"Equipamento '{epi.nome}' cadastrado com sucesso no almoxarifado!"
            )
            # Permanece na tela de cadastro para novos registros
            return redirect('epi_create')
        else:
            messages.error(
                request,
                "Falha ao cadastrar o equipamento. Por favor, verifique os erros destacados abaixo."
            )
    else:
        form = EPIForm()

    context = {
        'form': form,
        'titulo_pagina': 'Cadastrar Novo Equipamento (EPI)',
        'is_edicao': False,
    }
    return render(request, 'equipamentos/epi_form.html', context)


@login_required
def epi_update(request, pk):
    """
    Edição de Equipamentos (EPIs).
    Permite atualizar dados e estoque de um EPI já cadastrado.
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
                "Falha ao salvar as alterações do equipamento. Corrija os erros destacados."
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
@login_required
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

@login_required
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


@login_required
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


@login_required
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
                usuario_responsavel=request.user,
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


@login_required
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
@login_required
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
