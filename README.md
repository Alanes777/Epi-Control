# 🦺 EPI Control — Sistema de Gerenciamento de EPIs

Sistema web completo desenvolvido para o controle, inventário, catalogação e acompanhamento de **Empréstimos e Devoluções de Equipamentos de Proteção Individual (EPIs)** para o setor de **Construção Civil** e Saúde e Segurança do Trabalho (SST).

> **Projeto Acadêmico** — Curso Técnico em Desenvolvimento de Sistemas  
> **Foco do Projeto:** Funcionamento correto das funcionalidades, validação rigorosa no servidor, organização do código no padrão MVT do Django e persistência de dados em banco relacional SQLite.

---


---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.13 e framework **Django 6** (arquitetura Model-View-Template).
- **Banco de Dados:** **SQLite**, integrado nativamente com o ORM do Django.
- **Frontend:** HTML5 semântico, CSS3 personalizado e **Bootstrap 5** (via CDN), além de ícones do **Bootstrap Icons**.
- **Versionamento:** **Git** estruturado e publicado no GitHub: [https://github.com/Alanes777/Epi-Control](https://github.com/Alanes777/Epi-Control).
- **Containerização:** **Dockerfile** funcional com automação de migrações e inicialização do servidor.

---

## 📋 Telas e Requisitos Entregues

### 1. 🖥️ Tela Base (Sidebar e Perfil de Usuário)
- Menu de navegação lateral (Sidebar) persistente com ícones e links rápidos.
- Exibição de foto e identificação do usuário logado: **Carlos R. Mendes — Técnico em SST (Reg. MTE: 004128/SP)**, atendendo ao requisito sem necessidade de autenticação complexa.
- Barra superior informativa e notificações de feedback via alerts do Bootstrap 5.

### 2. 👷 Gerenciamento de Colaboradores
- **Cadastro:** Campos com validação obrigatória (`nome`, `matrícula`, `setor`), e-mail com validação de formato e bloqueio de matrícula duplicada.
- **Fluxo Contínuo:** Após cadastrar com sucesso, o sistema permanece na tela de cadastro para agilizar múltiplos registros.
- **Listagem e Pesquisa:** Tabela responsiva com busca por nome completo ou parcial no banco de dados.
- **Edição:** Permite atualizar os dados do colaborador, mantendo sua matrícula ou impedindo colisão com terceiros.
- **Exclusão Segura:** Modal interativo de confirmação em Bootstrap, com exclusão via requisição **POST com CSRF** (bloqueio rigoroso de GET via erro 405).

### 3. 🛡️ Gerenciamento de Equipamentos (EPIs)
- **Cadastro e Estoque:** Nome do EPI, descrição técnica, número do Certificado de Aprovação (C.A.) e saldo em estoque.
- **Fluxo Contínuo:** Permanece na tela após o cadastro.
- **Edição e Exclusão Segura:** Edição de dados e exclusão protegida com modal de confirmação.

### 4. 📋 Controle de EPI (Empréstimos e Devoluções)
- **Relacionamento com Chaves Estrangeiras:** Vínculo direto entre `Colaborador` e `EPI`.
- **Controle de Datas:** Registra data de entrega, data prevista de devolução e data efetiva de devolução.
- **Regra de Data Futura:** Para equipamentos emprestados, a data prevista para devolução deve ser estritamente posterior à data e hora atuais.
- **Ciclo de 5 Status:**
  - `Emprestado`: Uso temporário que deve retornar ao departamento.
  - `Fornecido`: Entrega definitiva ao colaborador.
  - `Devolvido`: Retorno do EPI com opção de reintegrar ao estoque.
  - `Danificado`: Avaria durante a execução de obras civis.
  - `Perdido`: Extravio do equipamento.
- **Restrição de Criação:** No formulário de cadastro, os status `Devolvido`, `Danificado` e `Perdido` ficam **ocultos**, permitindo selecionar apenas `Emprestado` ou `Fornecido`.
- **Tela de Atualização de Status:**
  - Carrega todos os 5 status para seleção.
  - **Bloqueio de alteração:** Colaborador, Equipamento, Data de Entrega e Data Prevista são somente leitura para auditoria.
  - Exibição dinâmica em JavaScript dos campos de **Data de Devolução** e **Observação** apenas quando selecionados `Devolvido`, `Danificado` ou `Perdido`.
- **Filtro Avançado Tipo AND:**
  - Permite filtrar simultaneamente por `Colaborador` **AND** `EPI` **AND** `Status`.
  - Exemplo: Consultar um operário específico com status `Emprestado` para saber exatamente o que ele ainda não devolveu.
- **Sinalização Visual de Atraso:** Alerta visual vermelho ("Prazo Vencido") quando o prazo previsto foi ultrapassado.

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

5. **Popular com Dados Iniciais da Construção Civil (Opcional):**
   ```bash
   python manage.py popular_banco
   ```

6. **Iniciar o Servidor:**
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

---

## 🌐 Endereços das Páginas do Sistema

| Módulo / Página | Rota / URL | Descrição |
| :--- | :--- | :--- |
| **Página Inicial** | `/` | Dashboard de indicadores e visão geral da obra |
| **Colaboradores — Listagem** | `/colaboradores/` | Tabela com busca por nome e exclusão segura |
| **Colaboradores — Cadastro** | `/colaboradores/novo/` | Formulário para registrar novo colaborador |
| **Colaboradores — Edição** | `/colaboradores/<id>/editar/` | Atualização de dados cadastrais |
| **Equipamentos — Catálogo** | `/equipamentos/` | Inventário de EPIs da construtora e C.A. |
| **Equipamentos — Cadastro** | `/equipamentos/novo/` | Formulário para registrar novo EPI |
| **Equipamentos — Edição** | `/equipamentos/<id>/editar/` | Atualização de estoque e especificações |
| **Controle de EPI — Listagem** | `/emprestimos/` | Histórico com filtros simultâneos **AND** e status |
| **Controle de EPI — Novo Empréstimo** | `/emprestimos/novo/` | Saída de EPI com data futura e baixa de estoque |
| **Controle de EPI — Atualizar Status** | `/emprestimos/<id>/editar/` | Atualização de status (Devolvido, Danificado, etc.) |
| **Tela de Relatórios (Filtro AND)** | `/relatorios/` | Pesquisa combinada (Colaborador AND EPI AND Status) e auditoria SST |
| **Painel Administrativo** | `/admin/` | Gestão interna pelo Django Admin |

---

## 🧪 Testes Automatizados

O sistema conta com **24 testes automatizados** cobrindo todos os fluxos críticos dos módulos:
```bash
python manage.py test
```
**Resultado:**
```text
Ran 24 tests in 0.430s - OK
```

---

## 🐳 Execução com Docker

```bash
# Construir a imagem
docker build -t epi-control .

# Executar o contêiner
docker run -p 8000:8000 --name epi-app epi-control
```
