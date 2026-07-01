# 2clix Backlog CLI

Visibilidade operacional do time de desenvolvimento via Azure DevOps — daily, refinamento, WIP, bloqueios e incidentes em menos de 10 segundos no terminal.

---

## Pré-requisitos

| Requisito | Versão mínima |
|-----------|--------------|
| Python | 3.11+ |
| Acesso ao Azure DevOps | `2clix` org |
| (Opcional) Anthropic API Key | para o comando `ask` |

---

## Configuração do ADO_PAT

### 1. Gerar o Personal Access Token

1. Acesse **dev.azure.com/2clix** e clique no seu avatar → **Personal Access Tokens**
2. Clique em **+ New Token**
3. Preencha:
   - **Name:** `backlog-cli` (ou qualquer nome descritivo)
   - **Organization:** `2clix`
   - **Expiration:** 1 ano (máximo permitido)
   - **Scopes:** selecione **Custom defined** e marque apenas:
     - `Work Items` → **Read**
4. Clique em **Create** e **copie o token** (ele não será exibido novamente)

### 2. Criar o arquivo `.env`

```bash
cp .env.example .env
```

Edite `.env` e preencha:

```env
ADO_PAT=cole_seu_token_aqui
ANTHROPIC_API_KEY=cole_sua_chave_aqui   # opcional — só para o comando ask
```

> **Segurança:** `.env` está no `.gitignore` e nunca deve ser commitado.

---

## Instalação

```bash
# Clone o repositório
git clone git@github.com:2clix/ado.git
cd ado

# (Opcional) ambiente virtual
python3 -m venv .venv && source .venv/bin/activate

# Dependências de produção (apenas anthropic, para o ask)
pip install -e .

# Dependências de desenvolvimento (testes, lint, type check)
pip install -e ".[dev]"
```

> O CLI não precisa de instalação para uso diário — `python3 backlog.py` funciona diretamente com a stdlib.

---

## Uso

```bash
python3 backlog.py              # menu interativo (recomendado)
python3 backlog.py resumo       # resumo geral do backlog
python3 backlog.py daily        # pauta da daily por dev
python3 backlog.py refinamento  # demandas em refinamento (tag: dev), mais antigas primeiro
python3 backlog.py jornal       # jornal semanal de demandas
python3 backlog.py gargalos     # gargalos e bloqueios críticos
python3 backlog.py wip          # WIP por pessoa
python3 backlog.py parados      # items sem movimento há +5 dias
python3 backlog.py tasks        # tasks por dev (PBI → subtasks)
python3 backlog.py ask          # chat com Claude sobre o backlog (requer ANTHROPIC_API_KEY)
```

### Navegação no menu interativo

```
1 → Resumo       5 → Gargalos
2 → Daily        6 → WIP
3 → Refinamento  7 → Parados
4 → Jornal       8 → Ask (IA)
                 9 → Tasks
```

### Hyperlinks no terminal

Os `#IDs` são links OSC-8 clicáveis que abrem o item no navegador — suportado em **iTerm2**, **VSCode integrated terminal** e **macOS Terminal** (≥ Big Sur).

---

## Personalização

### Adicionar ou remover um desenvolvedor

Edite as listas no topo de `backlog.py`:

```python
DEVS = [
    ("Nome Completo",  "Papel",  "fragmento_do_login"),
    # fragmento é qualquer parte do campo AssignedTo no ADO
    # ex: "Baena" para "Rafael Baena", "lucas.osik" para login exato
]
```

As listas disponíveis são `DEVS`, `QA_DEVS`, `INTEGRACOES` e `GESTAO`. A ordem define a sequência de exibição no daily.

### Adicionar uma nova query ADO

1. No Azure DevOps, crie a query e copie seu **ID** (UUID na URL da query)
2. Adicione em `QUERIES`:

```python
QUERIES = {
    ...
    "Minha Query": ("uuid-da-query", "Nome do Projeto ADO"),
}
```

3. Se a query deve aparecer no daily, adicione também em `DAILY_QUERIES`:

```python
DAILY_QUERIES = [
    ...,
    "Minha Query",
]
```

---

## Evolução do projeto

Este projeto segue **Spec-Driven Development (SDD)**. Antes de implementar qualquer coisa nova, leia `CLAUDE.md`.

### Fluxo resumido

```
Ideia → /nova-feature → spec.md → tasks.md → código → PR
```

### Quality gates (rodar antes de abrir PR)

```bash
python3 -m pytest tests/ -v                          # testes
python3 -m pytest tests/ --cov=src --cov-report=term # cobertura ≥ 60%
ruff check . && ruff format --check .                # lint e formato
mypy src/                                            # type check
bandit -r src/ -ll                                   # segurança
```

### Onde escrever

| O que | Onde |
|-------|------|
| Decisão arquitetural durável | `docs/architecture/adr/` |
| Estado atual / próximo passo | `docs/STATE.md` |
| Novo termo de negócio | `docs/glossary.md` |
| Feature em andamento | `specs/NNNN-nome/spec.md` |

---

## Estrutura do projeto

```
ado/
├── backlog.py          # CLI principal (ponto de entrada)
├── .env                # credenciais locais (não commitado)
├── .env.example        # template de credenciais
├── pyproject.toml      # dependências e configuração de ferramentas
├── src/                # código em camadas (DDD — em evolução)
│   ├── domain/         # regras de negócio puras
│   ├── application/    # casos de uso
│   ├── infrastructure/ # adapters ADO e Anthropic
│   └── interfaces/     # CLI
├── tests/              # testes pytest
├── specs/              # specs das features (SDD)
├── docs/               # documentação viva
│   ├── STATE.md        # memória de trabalho entre sessões
│   ├── product/        # visão e roadmap
│   └── architecture/   # ADRs e context map
└── logs/               # executions.jsonl (local, não versionado)
```

---

## Suporte

Dúvidas sobre configuração ou uso → **Rafael Baena** (Gestão Dev)
Bugs e melhorias → abra uma issue neste repositório
