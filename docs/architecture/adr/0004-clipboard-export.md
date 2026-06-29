---
name: adr-0004
description: ADR — exportar relatórios para clipboard como canal de comunicação com stakeholders.
alwaysApply: false
---

# ADR-0004: Exportar relatórios para clipboard (via `--clip`)

- **Status:** aceito
- **Data:** 2026-06-29
- **Decisores:** Rafael Baena

## Contexto
Stakeholders não têm acesso ao terminal. O gerente precisa compartilhar relatórios (jornal,
resumo, daily) via Teams, e-mail ou mensagem. Hoje exige copiar manualmente o output do terminal.

## Decisão
Adicionar flag `--clip` (ou `-c`) a todos os comandos de relatório. Quando ativa, copia o
output (sem ANSI/cores) para o clipboard do sistema operacional usando `pbcopy` (macOS).

## Alternativas descartadas
- **Webhook Teams:** alta complexidade, requer configuração por canal, fora dos non-goals
- **Exportar para arquivo .md:** útil, mas adiciona um passo (abrir e copiar o arquivo)
- **`pbcopy` + output limpo:** simples, zero dependência externa, uma flag só

## Consequências
- **+** Um comando → clipboard → colar no Teams/e-mail
- **+** Zero dependência adicional (pbcopy é nativo no macOS)
- **−** Funciona só no macOS por ora (Linux precisaria de `xclip`/`xsel`)
- Revisitar para suporte Linux se o time usar Linux (substituir por ADR novo)
