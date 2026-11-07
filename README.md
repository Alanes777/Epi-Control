# 🦺 EPI Control — Sistema de Gerenciamento de EPIs

Sistema web completo desenvolvido para o controle, inventário, catalogação, acompanhamento de **Empréstimos e Devoluções de Equipamentos de Proteção Individual (EPIs)** e **Controle de Acesso / Autenticação** para o setor de **Construção Civil** e Saúde e Segurança do Trabalho (SST).

> **Projeto Acadêmico** — Curso Técnico em Desenvolvimento de Sistemas  
> **Foco do Projeto:** Funcionamento correto das funcionalidades, validação rigorosa no servidor, segurança de rotas, controle de acesso baseado em grupos e permissões no Django Admin, organização do código no padrão MVT do Django e persistência de dados em banco relacional SQLite.

---

## 🎯 Contextualização e Desafio do Sistema

Uma empresa de construção civil da região identificou a necessidade de melhorar a gestão dos equipamentos de proteção individual (EPIs) utilizados pelos colaboradores nas obras. Em auditoria interna, observou-se que colaboradores esqueciam seus EPIs em casa ou não os retiravam com o setor de SST, gerando riscos e não conformidades com as normas regulamentadoras (NR-06, NR-18 e NR-35).

O **EPI Control** foi desenvolvido por alunos do curso de Desenvolvimento de Sistemas para solucionar esse desafio, assegurando um ambiente de trabalho mais seguro e em total conformidade com a legislação trabalhista:

1. **Autenticação & Controle de Acesso:** Login/Logout protegidos com expiração de sessão e bloqueio automático de acesso anônimo a todas as rotas internas.
2. **Controle de Usuários e Permissões no Django Admin:** Criação de grupos com permissões granulares de **adicionar, editar, visualizar e excluir** dados de modelos, como demonstrado com o model **Setor**.
3. **Tela Base / Layout com Menu Lateral:** Navegação ágil por sidebar com identificação dinâmica do usuário logado (nome, grupo/função e botão de logout).
4. **Cadastro e Gestão de Colaboradores:** Controle de operários por frente de trabalho (alvenaria, estruturas, armação, elétrica) com validação de matrícula única.
5. **Catálogo e Estoque de EPIs:** Gestão de equipamentos com número de Certificado de Aprovação (C.A.), controle quantitativo no almoxarifado e validade.
6. **Controle de EPI / Cautelas e Devoluções:** Ciclo completo de vida dos equipamentos (Emprestado, Fornecido, Devolvido, Danificado, Perdido), validação de devolução futura e filtros combinados do tipo **AND**.

---

## 🔐 Autenticação, Controle de Usuários e Permissões

### 1. Sistema de Login e Logout
- **Tela de Login Personalizada (`/login/`):** Estilizada com Bootstrap 5, feedback visual de mensagens de erro ou boas-vindas, campo para redirecionamento após autenticação (`next`).
- **Logout Seguro (`/logout/`):** Encerramento completo de sessão com mensagem de confirmação e redirecionamento para o login.
- **Proteção Total de Rotas:** Implementada via `core.middleware.AuthRequiredMiddleware`. **Todas as rotas do sistema são estritamente protegidas**, exigindo que o usuário esteja autenticado. As únicas exceções públicas são a tela de login (`/login/`), a rota de logout (`/logout/`), o Django Admin (`/admin/` — que possui seu próprio controle de acesso) e os arquivos estáticos. Tentativas de acesso não autenticado a rotas protegidas redirecionam automaticamente para `/login/?next=<rota>`.

### 2. Controle de Usuários e Grupos no Django Admin (Model Setor)
- **Model `Setor`:** Cadastrado no sistema e registrado no Django Admin para representar as frentes de trabalho da construtora (Canteiro de Obras, Alvenaria, Armação de Aço, Instalações Elétricas e Hidráulicas, Acabamento).
- **Grupos com Permissões Granulares:** No Django Admin (`/admin/auth/group/`), é possível criar grupos e conceder exatamente as 4 permissões do Django para qualquer model:
  - `core.add_setor` — Adicionar Setor
  - `core.change_setor` — Editar Setor
  - `core.view_setor` — Visualizar Setor
  - `core.delete_setor` — Excluir Setor
- **Tela de Controle de Usuários (`/usuarios/`):** Painel interno que lista todos os usuários cadastrados, seus grupos de acesso, status (ativo/inativo), data de último login e links rápidos para o Django Admin.

### 🔑 Credenciais Pré-Configuradas para Avaliação:

| Usuário | Senha | Perfil / Nível | O que faz no sistema / Django Admin |
| :--- | :--- | :--- | :--- |
| **`admin`** | `admin123` | **Superadministrador** | Acesso completo a todas as telas do sistema e a todos os modelos do Django Admin. |
| **`carlos.sst`** | `carlos123` | **Técnico em SST** | Pertence ao grupo *Técnicos de SST*. Realiza cautelas, controle de EPI e cadastros operacionais. |
| **`gestor.setor`** | `gestor123` | **Gestor de Setores (Staff)** | Pertence ao grupo *Gestores de Setor*. No Django Admin (`/admin/`), possui permissões estritas para **adicionar, editar, visualizar e excluir o model Setor**. |

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.13 e framework **Django 6** (arquitetura Model-View-Template).
- **Autenticação:** `django.contrib.auth`, com senhas criptografadas por PBKDF2 e middleware de segurança customizado.
- **Banco de Dados:** **SQLite**, integrado nativamente com o ORM do Django.
- **Frontend:** HTML5 semântico, CSS3 personalizado e **Bootstrap 5** (via CDN), além de ícones do **Bootstrap Icons**.
- **Versionamento:** **Git** estruturado e publicado no GitHub: [https://github.com/Alanes777/Epi-Control](https://github.com/Alanes777/Epi-Control).
- **Containerização:** **Dockerfile** funcional com automação de migrações e inicialização do servidor.

---

## 📋 Telas e Requisitos Entregues

### 1. 🖥️ Tela Base (Sidebar e Usuário Dinâmico)
- Menu de navegação lateral (Sidebar) persistente com links rápidos e ícones.
- Exibição dinâmica do usuário logado: nome completo, perfil/grupo de acesso, username e botão de logout rápido.
- Barra superior informativa com saudação personalizada e botão de encerramento de sessão.

### 2. 👷 Gerenciamento de Colaboradores
- **Cadastro:** Validação de campos obrigatórios (`nome`, `matrícula`, `setor`), e-mail válido e bloqueio de matrícula duplicada.
- **Fluxo Contínuo:** Permanece na tela após cadastrar para novos registros.
- **Listagem e Pesquisa:** Tabela responsiva com busca por nome completo ou parcial no banco de dados.
- **Edição & Exclusão Segura:** Edição de dados e exclusão confirmada por modal Bootstrap via requisição **POST com CSRF**.

### 3. 🛡️ Gerenciamento de Equipamentos (EPIs)
- **Cadastro e Estoque:** Nome do EPI, descrição técnica, número do Certificado de Aprovação (C.A.) e saldo em estoque.
- **Edição e Exclusão Segura:** Edição de dados e exclusão protegida com modal de confirmação.

### 4. 📋 Controle de EPI (Empréstimos e Devoluções)
- **Relacionamento com Chaves Estrangeiras:** Vínculo direto entre `Colaborador`, `EPI` e `User` (técnico responsável).
- **Regra de Data Futura:** Para equipamentos emprestados, a data prevista para devolução deve ser estritamente posterior à data e hora atuais.
- **Ciclo de 5 Status:** `Emprestado`, `Fornecido`, `Devolvido`, `Danificado`, `Perdido`.
- **Restrição de Criação:** No formulário de cadastro, os status `Devolvido`, `Danificado` e `Perdido` ficam **ocultos** (apenas `Emprestado` ou `Fornecido` permitidos na saída).
- **Tela de Atualização de Status:**
  - Carrega todos os 5 status para seleção.
  - **Bloqueio de alteração (`disabled`):** Colaborador, Equipamento, Data de Entrega e Data Prevista são somente leitura para auditoria.
  - Exibição dinâmica em JavaScript dos campos de **Data de Devolução** e **Observação** apenas quando selecionados `Devolvido`, `Danificado` ou `Perdido`.
- **Filtro Avançado Tipo AND:** Filtra simultaneamente por `Colaborador` **AND** `EPI` **AND** `Status`.
- **Tela de Relatórios (`/relatorios/`):** Relatório de auditoria SST com indicadores e suporte a impressão/PDF.

---

## 🚀 Como Executar o Projeto Localmente

### 1. Inicialização Rápida no Windows (1 Clique)
Basta dar um duplo clique no arquivo **`executar.bat`**. O servidor iniciará e o navegador abrirá automaticamente em:  
👉 **`http://127.0.0.1:8000/login/`**

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

5. **Popular com Dados Iniciais, Usuários e Grupos (Recomendado):**
   ```bash
   python manage.py popular_banco
   ```

6. **Iniciar o Servidor:**
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

---

## 🌐 Endereços das Páginas do Sistema

| Módulo / Página | Rota / URL | Acesso | Descrição |
| :--- | :--- | :--- | :--- |
| **Login** | `/login/` | Público | Autenticação no sistema com credenciais de usuário |
| **Logout** | `/logout/` | Público | Encerra a sessão e redireciona para a tela de login |
| **Página Inicial** | `/` | Protegido | Dashboard de indicadores e visão geral da obra |
| **Controle de Usuários** | `/usuarios/` | Protegido | Painel com listagem de usuários e atalhos para grupos |
| **Colaboradores — Listagem** | `/colaboradores/` | Protegido | Tabela com busca por nome e exclusão segura |
| **Colaboradores — Cadastro** | `/colaboradores/novo/` | Protegido | Formulário para registrar novo colaborador |
| **Colaboradores — Edição** | `/colaboradores/<id>/editar/` | Protegido | Atualização de dados cadastrais |
| **Equipamentos — Catálogo** | `/equipamentos/` | Protegido | Inventário de EPIs da construtora e C.A. |
| **Equipamentos — Cadastro** | `/equipamentos/novo/` | Protegido | Formulário para registrar novo EPI |
| **Equipamentos — Edição** | `/equipamentos/<id>/editar/` | Protegido | Atualização de estoque e especificações |
| **Controle de EPI — Listagem** | `/emprestimos/` | Protegido | Histórico com filtros simultâneos **AND** e status |
| **Controle de EPI — Novo Empréstimo** | `/emprestimos/novo/` | Protegido | Saída de EPI com data futura e baixa de estoque |
| **Controle de EPI — Atualizar Status** | `/emprestimos/<id>/editar/` | Protegido | Atualização de status (Devolvido, Danificado, etc.) |
| **Tela de Relatórios (Filtro AND)** | `/relatorios/` | Protegido | Pesquisa combinada (Colaborador AND EPI AND Status) |
| **Painel Administrativo** | `/admin/` | Staff/Superuser | Gestão interna de Usuários, Grupos, Permissões e Setores |

---

## 🧪 Testes Automatizados

O sistema conta com **31 testes automatizados** cobrindo autenticação, bloqueio de rotas, grupos e permissões no model Setor, além de todos os CRUDs:
```bash
python manage.py test
```
**Resultado:**
```text
Ran 31 tests in 53.917s - OK
```

---

## 🐳 Execução com Docker

```bash
# Construir a imagem
docker build -t epi-control .

# Executar o contêiner
docker run -p 8000:8000 --name epi-app epi-control
```
