---
name: assessment
description: Estado atual do projeto (brownfield as-is). Puxe ao planejar refatorações ou mapear gaps.
alwaysApply: false
---

# Assessment — Estado atual (as-is)

> Produzido no kickoff brownfield em 2026-06-29. Retrato do projeto antes da esteira SDD.

## Stack atual
- Python 3 (stdlib pura: `urllib`, `json`, `base64`, `collections`, `datetime`)
- Sem dependências externas além do SDK Anthropic (via HTTP manual)
- Sem gerenciador de pacotes em uso (agora: `pyproject.toml` adicionado)

## Estrutura
- **1 arquivo único:** `backlog.py` (611 linhas)
- Sem separação de camadas — HTTP, lógica de negócio, formatação e CLI estão no mesmo arquivo
- Sem testes, sem type hints, sem lint

## Funcionalidades existentes (7 comandos)
| Comando | O que faz |
|---------|-----------|
| `resumo` | Visão geral por estado e por query |
| `daily` | Pauta por dev: feitos, em andamento, bloqueados, parados |
| `jornal` | Relatório semanal de demandas por estado |
| `gargalos` | WIP por pessoa + bloqueados + P0/P1 parados |
| `wip` | WIP detalhado por pessoa |
| `parados` | Items sem movimento há +3 dias |
| `ask` | Chat com Claude em linguagem natural sobre o backlog |

## Queries ADO (10 filas)
Esteira Dev · Esteira Dev Flat · Esteira Dev Reprov · Esteira DevOps · Esteira Front End ·
Esteira QA · Integrações · Refinamento · Espera Sprint · Jornal

## Gap analysis vs padrão SDD

| Eixo | Estado atual | Gap | Risco |
|------|-------------|-----|-------|
| Tech stack | stdlib pura, ok | Sem type hints, sem lint | médio |
| Arquitetura | monolito sem camadas | Lógica misturada, difícil testar | alto |
| Infra/Deploy | execução local manual | PAT em env var (resolvido) | baixo |
| Qualidade | sem testes, sem lint | Nenhum gate automatizado | alto |
| Observabilidade | nenhuma | Sem logs estruturados | baixo |

## Dívidas técnicas e riscos
- **Alto:** lógica de domínio (WorkItem, filtros, cálculos) misturada com I/O e formatação
- **Alto:** sem testes — qualquer mudança pode quebrar silenciosamente
- **Médio:** sem type hints — erros de tipo só aparecem em runtime
- **Médio:** não há como filtrar tasks por PBI pai (principal dor relatada)
- **Baixo:** `cmd_ask` sem tratamento de erro adequado quando API key está vazia

## Decisões históricas → ADRs retroativos
- Stdlib pura para HTTP (sem requests) → [ADR-0002](adr/0002-stdlib-http.md)
- Python como linguagem do CLI → [ADR-0003](adr/0003-python-cli.md)
