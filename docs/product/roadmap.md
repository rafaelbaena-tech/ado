---
name: roadmap
description: Roadmap Now/Next/Later do projeto. Puxe ao planejar features ou revisar prioridades.
alwaysApply: true
---

# Roadmap — 2clix Backlog CLI

> Revisado no kickoff brownfield em 2026-06-29. Capacidade baseada no uso atual (Rafael, solo).
> Horizonte: enquanto ADO for a ferramenta de gestão da 2clix.

## Agora (Now) — próximas 2 semanas

| Item | Valor | Esforço | Dono | Pronto quando |
|------|-------|---------|------|---------------|
| **Filtro tasks por PBI** | ★★★ | médio | Rafael | `backlog.py tasks <PBI-id>` mostra tasks filhas |
| **Exportar relatório para clipboard** | ★★★ | pequeno | Rafael | qualquer comando com `--clip` copia o output |
| **Ativar comando `ask` (Claude)** | ★★ | trivial | Rafael | ANTHROPIC_API_KEY preenchida + teste manual |

## Próximo (Next) — após o Now

| Item | Valor | Esforço | Dono | Depende de |
|------|-------|---------|------|------------|
| Migrar lógica de domínio para `src/domain/` | ★★ | médio | Rafael | — |
| Testes unitários para regras de negócio | ★★ | médio | Rafael | migração domínio |
| Filtro por sprint / período | ★★ | médio | Rafael | migração domínio |
| Relatório de sprint (fechamento) | ★★ | médio | Rafael | filtro por sprint |

## Depois (Later) — quando houver clareza

| Item | Valor | Esforço | Observação |
|------|-------|---------|------------|
| Agendamento / notificação automática | ★ | alto | Avaliar quando rotina estiver estável |
| Integração MCP ADO | ★★ | alto | Depende de MCP server disponível |
| Transição para plataforma definitiva | — | — | Quando a plataforma 2clix estiver pronta |

## Adoção incremental do SDD
- Próxima feature já nasce com `spec.md` + `tasks.md`
- Backfill de ADRs para decisões históricas (stdlib HTTP, Python CLI)
- Refatoração de `backlog.py` → camadas DDD **só quando houver spec aprovada**
