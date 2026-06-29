---
name: adr-0002
description: ADR retroativo — uso de stdlib urllib para chamadas HTTP ao ADO e Anthropic.
alwaysApply: false
---

# ADR-0002: Usar stdlib urllib para HTTP (sem dependências externas)

- **Status:** aceito
- **Data:** 2026-06-29 (retroativo — decisão tomada na criação do backlog.py)
- **Decisores:** Rafael Baena

## Contexto
O projeto é um CLI de uso pessoal/interno. A alternativa natural seria usar `requests` ou
`httpx`, mas adicionar dependências externas aumenta a fricção de instalação e manutenção
em um script que precisa rodar em qualquer máquina com Python 3.

## Decisão
Usar `urllib.request` da stdlib para todas as chamadas HTTP (ADO e Anthropic API).
Sem dependências externas de HTTP.

## Consequências
- **+** Zero dependências externas para o core do CLI
- **+** Funciona com `python3 backlog.py` sem `pip install`
- **−** Código de HTTP mais verboso que `requests`/`httpx`
- **−** Sem retry automático, sem timeout granular por operação
- Revisitar se o volume de integrações crescer muito (substituir por ADR novo)
