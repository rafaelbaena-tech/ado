---
name: vision
description: Visão do produto, North Star e non-goals. Puxe ao abrir feature nova ou roadmap.
alwaysApply: true
---

# Visão do produto — 2clix Backlog CLI

## Contexto estratégico
Este projeto é a **memória operacional do fluxo Scrum da 2clix enquanto a plataforma definitiva
de gestão está sendo construída**. O Azure DevOps é a ferramenta de suporte durante essa
transição — o CLI maximiza o valor extraído do ADO até que o sistema proprietário esteja pronto.

## Problema
O gerente de desenvolvimento da 2clix acompanha 10+ filas de trabalho no Azure DevOps
diariamente. Navegar pelo ADO é lento, não oferece visão consolidada por pessoa e não gera
relatórios prontos para stakeholders. A falta de visibilidade de tasks vinculadas a PBIs
dificulta entender o progresso real de uma entrega.

## Para quem
- **Rafael Baena** (Gestão Dev) — uso diário: daily, acompanhamento de gargalos e bloqueios
- **Stakeholders / liderança 2clix** — consumidores dos relatórios exportados (jornal, resumo)

## North Star
> **Qualquer pessoa com acesso ao terminal consegue, em menos de 10 segundos, saber
> exatamente o que cada membro do time está fazendo, o que está travado e o que precisa
> de atenção — e compartilhar isso com um stakeholder com um único comando.**

## Goals
- Visão operacional consolidada do time (quem está em quê, WIP, bloqueios, parados)
- Relatórios prontos para stakeholders com exportação para clipboard
- Filtro de tasks vinculadas a PBIs para rastrear progresso real de entregas
- Assistente IA (Claude) para perguntas em linguagem natural sobre o backlog

## Non-goals (vinculante — não implementar)
- Substituir o Azure DevOps como ferramenta de gestão
- Criar ou editar WorkItems no ADO (somente leitura)
- Interface web, mobile ou desktop
- Automação de reuniões (agendamento, convites, atas automáticas)
- Integrações com ferramentas de terceiros além do ADO e Claude

## Métricas de sucesso
| Métrica | Baseline | Alvo |
|---------|----------|------|
| Tempo para gerar pauta da daily | ~5 min manual | < 10 seg com CLI |
| Relatório compartilhável para stakeholder | cópia manual do terminal | 1 comando → clipboard |
| Visibilidade de tasks por PBI | zero | filtro funcional no CLI |
