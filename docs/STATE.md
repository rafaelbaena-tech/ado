---
name: STATE
description: Memória de trabalho volátil — onde paramos, próximo passo, bloqueios.
alwaysApply: true
---

# STATE — Memória viva do projeto

> Memória de trabalho **entre sessões** (humanos e agentes). É **volátil**: atualizada o tempo
> todo. Diferente do **ADR** (decisão durável e imutável). Decisão estrutural → ADR; estado do
> trabalho → aqui. Atualize ao **pausar/encerrar**; leia ao **retomar**. Use a skill `/handoff`.

**Última atualização:** 2026-06-29 por Rafael Baena

## Em andamento / próximo passo
- Kickoff brownfield concluído ✓
- Próximo passo: abrir primeira feature com `/nova-feature` — **Filtro tasks por PBI** (maior dor relatada)

## Decisões recentes
- 2026-06-29: Kickoff brownfield concluído — vision, roadmap, assessment e ADRs gerados
- 2026-06-29: Cobertura mínima definida em 60% (foco em domínio) — [ADR implícito no TESTING.md]
- 2026-06-29: Clipboard export via `--clip` como canal de stakeholders — [ADR-0004](architecture/adr/0004-clipboard-export.md)
- 2026-06-29: stdlib HTTP mantido (sem requests) — [ADR-0002](architecture/adr/0002-stdlib-http.md)

## Bloqueios
- [ ] _nenhum bloqueio no momento_

## Ideias adiadas / backlog técnico
- Migrar `backlog.py` monolítico para arquitetura em camadas DDD (quando houver spec aprovada)
- Avaliar uso de `rich` para CLI mais elegante
- Considerar cache local das queries ADO para reduzir latência

## Todos soltos
- [ ] Preencher `ANTHROPIC_API_KEY` no `.env` para ativar o comando `ask`
- [ ] Rodar `/integracoes` para mapear Azure DevOps + Anthropic como MCPs (roadmap Later)
- [ ] Backfill de context-map.md com bounded contexts identificados no kickoff
