---
name: TESTING
description: Comandos de gate e convenções de teste. Puxe ao codar, validar ou montar CI.
alwaysApply: false
---

# TESTING — Como verificar o projeto

> **Fonte única dos comandos de gate** e das convenções de teste. É o que o **DoD**, a **CI** e os
> **subagentes** consomem para provar que uma task/feature está pronta — sem inspeção visual.

## Como rodar

| Nível            | Comando                                                      | Quando |
|------------------|--------------------------------------------------------------|--------|
| Unidade          | `python -m pytest tests/unit/ -v`                            | sempre, rápido |
| Integração       | `python -m pytest tests/integration/ -v`                     | adapters / repos / contratos |
| Aceite (UAT)     | `python -m pytest tests/acceptance/ -v`                      | um teste por `AC-N` da spec |
| Lint             | `ruff check .`                                               | pré-commit / CI |
| Format           | `ruff format --check .`                                      | pré-commit / CI |
| Type check       | `mypy src/ --strict`                                         | CI — sem findings bloqueantes |
| SAST/segurança   | `bandit -r src/ -ll`                                         | CI — sem findings médios/altos |
| Cobertura        | `python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=xml --cov-fail-under=60` | CI — relatório publicado no PR |

## Convenções
- Pirâmide: muitos testes de unidade, menos de integração, poucos de aceite.
- **Cada `AC-N` da spec tem um teste de aceite que é o seu gate.** Nomeie o teste com o ID:
  `test_ac_1_*` / `test_ac_2_*` para rastreabilidade spec → teste.
- Domínio não sobe infra; integração usa mocks de borda (`unittest.mock`, `pytest-httpx`).
- Análise estática: **mypy** (type check), **ruff** (lint/complexidade), **bandit** (SAST).
  Findings **bloqueantes** (barram o merge): mypy errors, bandit ≥ MEDIUM.
  Findings de **aviso** (entram como tendência em `metrics.md`): ruff warnings, bandit LOW.
- Cobertura mínima: **60%** — foco em `src/domain/` (regras de negócio, filtros, cálculos).

## Gates (Definition of Done executável)
- Uma **task** só vira `done` quando o **Gate (comando)** dela em `tasks.md` passa.
- Uma **feature** só faz merge quando todos os AC estão verdes + lint + type check limpos
  + análise estática sem findings bloqueantes + cobertura ≥ 80%.
- A **CI roda exatamente estes comandos** — falhar bloqueia o merge.

## O que a CI executa
Pipeline em ordem: `ruff check` → `mypy` → `bandit` → `pytest unit` → `pytest integration`
→ `pytest acceptance` → cobertura (mínimo 80%, relatório publicado como artefato do PR).
Mais a regra SDD: falha PR que altera código `src/` sem `spec.md` aprovada.

## Setup do ambiente
```bash
# Com uv (recomendado)
uv venv && uv pip install -e ".[dev]"

# Ou com pip
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## pyproject.toml (referência)
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-httpx>=0.30",
    "mypy>=1.10",
    "ruff>=0.5",
    "bandit[toml]>=1.8",
]

[tool.mypy]
strict = true

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.bandit]
skips = ["B101"]  # assert em testes

[tool.pytest.ini_options]
testpaths = ["tests"]
```
