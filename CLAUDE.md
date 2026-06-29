---
name: CLAUDE
description: Convenções do agente para a esteira SDD. Sempre ativo.
alwaysApply: true
---

# CLAUDE.md — Convenções para agentes de IA

Este projeto segue **Spec-Driven Development (SDD)**. Leia antes de implementar qualquer coisa.

## Início de sessão — carregue o contexto base
> Um hook **`SessionStart`** (`.claude/settings.json` → `.claude/hooks/load-context.sh`) injeta
> este contexto base **automaticamente** (garantia determinística). Se o hook estiver desativado,
> esta diretiva é o fallback — e como o `CLAUDE.md` é sempre carregado, ela cobre o caso.

**Garanta o contexto base antes da primeira tarefa — os docs `alwaysApply: true`:**
`docs/STATE.md` · `docs/product/vision.md` · `docs/product/roadmap.md` · e a `spec.md` da
feature ativa em `specs/`.

Todos os outros docs são `alwaysApply: false` — **não os leia agora**. Puxe cada um **sob demanda**,
quando a tarefa exigir, guiado pelo `description` no frontmatter dele.

## A spec é a fonte da verdade
- Implemente **a partir de** `specs/NNNN-*/spec.md`. Os critérios de aceite
  (Given/When/Then) são o contrato e o oráculo de teste.
- Se a spec for ambígua ou estiver errada, **pare e pergunte** — não adivinhe.
  Atualizar a spec é uma decisão consciente, não um efeito colateral do código.
- Nunca implemente além do escopo da spec. "Out of scope" é vinculante.

## Verificação de conhecimento (nunca invente)
Antes de afirmar como algo funciona, siga esta ordem — pare assim que tiver a resposta:
1. **Padrões do próprio codebase** (como já é feito aqui).
2. **Docs do projeto** (`specs/`, `docs/`, ADRs, glossário).
3. **MCP** de referência quando conectado.
4. **Web/doc oficial** da tecnologia.
5. **Não encontrou? Diga "não sei" e sinalize.** Nunca invente API, padrão ou comportamento —
   inventar causa falha em cascata. Incerteza explícita é melhor que um chute confiante.

## Ferramentas conectadas (MCP)
> **Mantido pela skill `/integracoes`.** Lista os MCP servers validados e quem os consome, para o
> roteamento de skills/rules. Vazio até a primeira conexão — rode `/integracoes` para preencher.

| MCP (`mcp__<servidor>__*`) | Conta/workspace validada | Skills que consomem |
|---|---|---|
| _nenhum ainda_ | — | — |

Regra: conexão ativa **não** autoriza uso. Confirme a conta/workspace antes de ler e **reconfirme
antes de qualquer escrita** (ver `/integracoes`). Só use um MCP presente na sessão (`mcp__<servidor>__*`).

## Tech stack — Python + IA
- **Linguagem:** Python 3.11+
- **Gerenciador de pacotes:** `pip` / `uv` (prefira `uv` quando disponível)
- **Testes:** `pytest` + `pytest-cov`
- **Lint/format:** `ruff check` / `ruff format`
- **Análise estática:** `mypy --strict`
- **SAST/segurança:** `bandit -r src/`
- **Cliente Claude:** `anthropic` SDK (`claude-sonnet-4-6` por padrão)
- **Azure DevOps:** `requests` ou stdlib `urllib` (já em uso em `backlog.py`)

### Comandos de uso frequente
```bash
python -m pytest tests/ -v              # testes
python -m pytest tests/ --cov=src --cov-report=term-missing  # cobertura
ruff check .                             # lint
ruff format --check .                   # format check
mypy src/                               # type check
bandit -r src/ -ll                       # SAST
```

### Quality gates
- Cobertura mínima: **60%** — foco na lógica de domínio (`src/domain/`)
- Análise estática: mypy sem erros, ruff sem findings
- SAST: sem findings de severidade média ou alta (bandit)
- Nenhum `SPEC_DEVIATION` pendente no merge

## Antes de codar — descubra o tier
Pergunta: *isso introduz decisão difícil de reverter ou nova fronteira de domínio?*
- **Trivial** (≤3 arquivos, sem decisão): só o PR (ou `quick/` se quiser deixar rastro).
- **Pequeno** (feature isolada, <10 tasks): exige `spec.md` + `tasks.md`.
- **Arquitetural** (novo bounded context, integração externa, decisão irreversível):
  exige `design.md` aprovado **antes** de implementar. Se não existir, pare e sinalize.

> **Escalonamento dinâmico:** mesmo quando `tasks.md` é dispensado, **sempre liste os passos
> atômicos inline antes de codar**. Se a lista passar de ~5 passos ou tiver dependências
> complexas, **PARE e crie um `tasks.md` formal** — o tier real era maior do que parecia.

## Linguagem ubíqua
- Use **exatamente** os termos de `docs/glossary.md` e do `domain.md` da feature.
  Mesmo nome no código, na spec e na conversa com o time. Não invente sinônimos.
- Termo novo → adicione ao glossário no mesmo PR.

## Arquitetura em camadas (regra de dependência)
`src/` segue DDD tático. A dependência aponta **só para dentro**:

```
interfaces → application → domain ← infrastructure
```

- `domain/` não importa NADA de framework, I/O, ou de outras camadas.
- `application/` orquestra casos de uso; depende só de `domain/`.
- `infrastructure/` implementa as portas definidas no domínio (repos, adapters, HTTP, SDKs).
- `interfaces/` é a borda (CLI, API, UI).

### Convenções Python por camada
- `domain/`: classes puras, `@dataclass`, nenhum `import` de infra/framework
- `application/`: casos de uso como funções ou classes simples; imports só de `domain/`
- `infrastructure/`: adapters ADO (`AzureDevOpsClient`), adapter Anthropic (`ClaudeClient`)
- `interfaces/`: CLI (argparse / rich / prompt_toolkit), sem lógica de negócio

## Disciplina de contexto e delegação
Cada doc declara no frontmatter sua política de carregamento:
- `alwaysApply: true` — **contexto base**, leia em toda sessão.
- `alwaysApply: false` — **sob demanda**; o campo `description` diz **quando** puxá-lo.

**Base (`alwaysApply: true`):** este `CLAUDE.md` · `docs/STATE.md` · `docs/product/vision.md` ·
`docs/product/roadmap.md` · a `spec.md` da feature ativa. Todo o resto é sob demanda.

### Orçamento de contexto (alvo)
- **Base (`alwaysApply: true`): ~15k tokens.** Mantenha enxuto.
- **Sob demanda: só o necessário.** Total carregado **< 40k**; reserve **160k+** para o trabalho.
- Estourou o orçamento? **Delegue a subagente** (contexto isolado).

## Divergência da spec (SPEC_DEVIATION)
Se durante a implementação você precisar fazer diferente do que a `spec.md` diz:
1. **Pare antes de seguir.** Marque no código/PR um comentário `# SPEC_DEVIATION: <motivo>`.
2. Decida com o dono da spec: ou **corrige o código** (a spec vence) ou **atualiza a spec**
   conscientemente (e registra ADR se for decisão difícil de reverter).
3. Nunca deixe código e spec divergentes em silêncio.

## Definition of Done
- [ ] Todos os critérios de aceite da `spec.md` passam — **verificados pelo gate executável**
      (`pytest tests/` + comandos de `docs/engineering/TESTING.md`), não por inspeção visual
- [ ] **Cobertura ≥ 80%**, com o **relatório anexado ao PR** (evidência, não inspeção)
- [ ] **mypy sem erros** + **ruff limpo** + **bandit sem findings médios/altos**
- [ ] Nenhum `SPEC_DEVIATION` pendente sem resolução
- [ ] Decisões difíceis de reverter viraram ADR em `docs/architecture/adr/`
- [ ] Glossário e `docs/architecture/context-map.md` atualizados se mudaram
- [ ] A spec reflete o que foi construído (ou a divergência está documentada)
- [ ] `docs/STATE.md` atualizado (próximo passo, decisões, bloqueios)

## Memória de trabalho — `docs/STATE.md`
- **STATE.md é memória volátil** (em andamento, próximo passo, bloqueios, todos); **ADR é memória
  durável** (decisão imutável). Não confunda.
- Atualize o STATE ao pausar/encerrar uma sessão e leia-o ao retomar. Ver a skill `/handoff`.

## Onde escrever
- Decisão arquitetural durável → novo ADR (`docs/architecture/adr/`), nunca edite ADR antigo.
- Estado do trabalho / próximo passo → `docs/STATE.md`.
- Termo de negócio → `docs/glossary.md`.
- Mudança de fronteira/contexto → `docs/architecture/context-map.md`.
