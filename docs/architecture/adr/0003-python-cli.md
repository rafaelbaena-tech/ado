---
name: adr-0003
description: ADR retroativo — Python como linguagem e CLI como interface do projeto.
alwaysApply: false
---

# ADR-0003: Python + CLI como stack e interface

- **Status:** aceito
- **Data:** 2026-06-29 (retroativo)
- **Decisores:** Rafael Baena

## Contexto
O projeto precisa de uma ferramenta rápida de uso diário para consultar o Azure DevOps.
O gerente já tem Python disponível e familiaridade com terminal.

## Decisão
Python 3 com interface CLI (argparse + menu interativo). Sem servidor, sem interface web.

## Consequências
- **+** Sem infraestrutura — roda localmente com `python3 backlog.py`
- **+** Iteração rápida: editar e rodar imediatamente
- **+** Alinhado com o stack de IA (Anthropic SDK é Python-first)
- **−** Uso limitado a quem tem acesso ao terminal e ao Python
- **−** Relatórios não são acessíveis via browser (mitigado pelo clipboard export)
