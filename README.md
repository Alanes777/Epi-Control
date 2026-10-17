# 🦺 EPI Control — Sistema de Gerenciamento de EPIs

Sistema web completo desenvolvido para o controle, inventário, catalogação e acompanhamento de **Empréstimos e Devoluções de Equipamentos de Proteção Individual (EPIs)** em uma empresa do setor têxtil.

> **Projeto Acadêmico** — Curso Técnico em Desenvolvimento de Sistemas  
> **Foco do Projeto:** Funcionamento correto das funcionalidades, validação no servidor, organização do código no padrão MVT do Django e persistência de dados em banco relacional SQLite.

---

## 👥 Integrantes do Grupo

Preencha os dados dos integrantes da equipe para entrega da atividade:

| Nome do Aluno | Matrícula / Registro | E-mail |
| :--- | :--- | :--- |
| `[Nome do Aluno 1]` | `[Matrícula 1]` | `[email1@escola.edu.br]` |
| `[Nome do Aluno 2]` | `[Matrícula 2]` | `[email2@escola.edu.br]` |
| `[Nome do Aluno 3]` | `[Matrícula 3]` | `[email3@escola.edu.br]` |
| `[Nome do Aluno 4]` | `[Matrícula 4]` | `[email4@escola.edu.br]` |

---

## 🎯 Contextualização e Objetivo do Sistema

Durante uma auditoria interna em uma indústria têxtil, foram identificadas falhas operacionais: alguns colaboradores esqueciam seus EPIs em casa ou deixavam de retirá-los no departamento de Saúde e Segurança do Trabalho (SST).

O **EPI Control** centraliza:
1. O cadastro e histórico dos colaboradores autorizados da fábrica.
2. O inventário e estoque dos equipamentos de proteção com controle de Certificado de Aprovação (C.A.).
3. O registro em tempo real de retiradas/cautelas e devoluções, com abatimento e reintegração automática ao estoque físico e alertas visuais de devoluções em atraso.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.13 e framework **Django 6** (arquitetura Model-View-Template).
- **Banco de Dados:** **SQLite**, integrado nativamente com o ORM do Django.
- **Frontend:** HTML5 semântico, CSS3 e **Bootstrap 5** (via CDN), além de ícones do **Bootstrap Icons**.
- **Versionamento:** **Git** estruturado e publicado no GitHub: [https://github.com/Alanes777/Epi-Control](https://github.com/Alanes777/Epi-Control).
- **Containerização:** **Dockerfile** funcional com automação de migrações e inicialização do servidor.

---

## 📋 Status dos Requisitos do Projeto

### ✅ Funcionalidades Totalmente Implementadas

- **RF01 — Cadastro de Colaboradores:** Formulário completo com validação de campos obrigatórios (`nome`, `matrícula`, `setor`), validação de unicidade da matrícula e formato de e-mail. Após o envio com sucesso, permanece na tela com formulário limpo para agilizar múltiplos cadastros.
- **RF02 — Consulta e Listagem de Colaboradores:** Tabela responsiva em Bootstrap com nome, matrícula, setor, cargo e e-mail.
- **RF03 — Pesquisa de Colaboradores:** Filtro dinâmico no banco de dados (`icontains`) que permite localizar colaboradores pelo nome completo ou por qualquer termo parcial.
- **RF04 — Edição de Colaboradores:** Carregamento dos dados atuais com validação prévia. A matrícula do próprio colaborador pode ser mantida, mas matrículas de terceiros são estritamente bloqueadas.
- **RF05 — Exclusão Segura com Confirmação:** Modal do Bootstrap 5 que exige confirmação explícita do usuário antes da exclusão. A operação é protegida por requisição **POST com token CSRF** (requisições GET são bloqueadas com erro 405).
- **RF06 — Cadastro, Consulta e Gestão de EPIs:** Módulo completo de inventário de EPIs. Permite cadastrar nome, descrição, número do Certificado de Aprovação (C.A.), saldo físico de estoque e validade, além de pesquisa dinâmica por nome/C.A., edição e exclusão segura com modal.
- **RF07 — Consulta de Empréstimos por Colaborador e Período:** Painel avançado de filtros permitindo consultar cautelas por colaborador específico, por status (`Ativo`, `Devolvido`) e por intervalo de datas (`data_inicio` e `data_fim`).
- **RF08 — Gestão de Usuários e Permissões:** Estrutura integrada com o sistema nativo de autenticação do Django (`django.contrib.auth`).
- **RF09 — Registro de Empréstimos e Devoluções de EPIs:**
  - **Empréstimo:** Seleção do colaborador e EPI com abatimento automático no estoque físico do almoxarifado e bloqueio caso a quantidade solicitada seja maior que o saldo em estoque.
  - **Devolução:** Modal interativo para registrar a data real de devolução, observações e opção de reintegrar as peças limpas de volta ao estoque do almoxarifado.
  - **Prazos:** Identificação automática de empréstimos com prazo de devolução vencido (badge vermelho "Prazo Vencido").

---

## 🚀 Como Executar o Projeto Localmente

### 1. Inicialização Rápida no Windows (1 Clique)
Basta dar um duplo clique no arquivo **`executar.bat`**. O servidor iniciará e o navegador abrirá automaticamente em:  
👉 **`http://127.0.0.1:8000`**

---

### 2. Execução pelo Terminal / PowerShell

1. **Clonar o Repositório:**
   ```bash
   git clone https://github.com/Alanes777/Epi-Control.git
   cd Epi-Control
   ```

2. **Criar e Ativar o Ambiente Virtual:**
   - No Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - No Linux / macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instalar Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar as Migrações do Banco:**
   ```bash
   python manage.py migrate
   ```

5. **Popular com Dados Iniciais da Indústria Têxtil (Opcional):**
   ```bash
   python manage.py popular_banco
   ```

6. **Iniciar o Servidor:**
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

---

## 🌐 Endereços das Páginas Principais

| Módulo / Página | Rota / URL | Descrição |
| :--- | :--- | :--- |
| **Página Inicial** | `/` | Visão geral do EPI Control e cards de navegação |
| **Colaboradores — Listagem** | `/colaboradores/` | Tabela com busca por nome e exclusão segura |
| **Colaboradores — Cadastro** | `/colaboradores/novo/` | Formulário para registrar novo colaborador |
| **Colaboradores — Edição** | `/colaboradores/<id>/editar/` | Formulário de edição de dados |
| **Equipamentos — Catálogo** | `/equipamentos/` | Inventário de EPIs, saldo de estoque e C.A. |
| **Equipamentos — Cadastro** | `/equipamentos/novo/` | Formulário para registrar novo EPI |
| **Equipamentos — Edição** | `/equipamentos/<id>/editar/` | Edição de estoque e especificações |
| **Empréstimos — Listagem** | `/emprestimos/` | Histórico com filtros por colaborador, status e período |
| **Empréstimos — Novo** | `/emprestimos/novo/` | Registro de cautela com baixa de estoque |
| **Painel Administrativo** | `/admin/` | Gestão interna pelo Django Admin |

---

## 🧪 Testes Automatizados

O sistema conta com **20 testes automatizados** cobrindo todos os fluxos críticos dos 3 módulos:
```bash
python manage.py test
```
**Resultado:**
```text
Ran 20 tests in 0.373s - OK
```

---

## 🐳 Execução com Docker

```bash
# Construir a imagem
docker build -t epi-control .

# Executar o contêiner
docker run -p 8000:8000 --name epi-app epi-control
```
Acesse: `http://localhost:8000`