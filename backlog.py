#!/usr/bin/env python3
"""
2clix Backlog CLI
Uso:
    python3 backlog.py              # menu interativo
    python3 backlog.py resumo       # resumo geral
    python3 backlog.py daily        # pauta da daily
    python3 backlog.py jornal       # jornal de demandas
    python3 backlog.py gargalos     # gargalos e bloqueios
    python3 backlog.py wip          # WIP por pessoa
    python3 backlog.py parados      # items sem movimento
    python3 backlog.py ask          # chat com Claude
"""
import os, sys, base64, json, urllib.request, urllib.parse
from datetime import datetime, timezone
from collections import defaultdict, Counter

# Carrega .env se existir (sem dependência externa)
_env = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env):
    with open(_env) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

PAT      = os.environ.get("ADO_PAT", "")
ORG      = "2clix"
PROJECT  = "Plataforma Qualidade"
ADO_HOST = "https://dev.azure.com"

QUERIES = {
    "Esteira Dev":         ("4bb03a89-b9bf-49fb-915e-4619f09a8440", PROJECT),
    "Esteira Dev Flat":    ("10e4fce2-3c83-4a8c-8805-b43c56e9bacc", PROJECT),
    "Esteira Dev Reprov":  ("585e2c79-0b53-4432-835c-04f3ad0a9cda", PROJECT),
    "Esteira DevOps":      ("7d0c77b6-e2e6-4e03-8336-9a472ce7d58c", PROJECT),
    "Esteira Front End":   ("a2605d42-a5e7-4763-88cb-432c8867bb6e", PROJECT),
    "Esteira QA":          ("eeda5015-7395-4b25-b0c6-bf31280f9ba5", PROJECT),
    "Integrações":         ("62e8aef3-b658-48f0-af7b-09abb7890996", "MONITORIA_IA"),
    "Refinamento":         ("6a95ca1e-4603-4a2d-ba76-a823097da1b5", PROJECT),
    "Espera Sprint":       ("33ede8e9-33c2-4dfb-9961-0157b1c0feb1", PROJECT),
    "Jornal":              ("bd80d41b-8279-48fd-abfb-61ae3dcd7050", PROJECT),
}
FIELDS = ",".join([
    "System.Id","System.Title","System.State","System.AssignedTo",
    "Microsoft.VSTS.Common.Priority","System.WorkItemType",
    "System.ChangedDate","System.CreatedDate",
    "Microsoft.VSTS.Scheduling.Effort","System.Tags",
])
DEVS = [
    ("Wesley Bernardes",  "Front Líder",         "Wesley"),
    ("Joao Junior",       "Back",                "Joao"),
    ("Danilo Plasicov",   "Back ★",              "Danilo"),
    ("Vinicius",          "Front",               "Vinicius"),
    ("lucas.osik",        "Front",               "lucas.osik"),
    ("Patrick",           "Back + IA",           "Patrick"),
]
QA_DEVS = [
    ("Rodrigo Tada",      "QA",                  "Tada"),
    ("fernando.alucema",  "QA",                  "fernando"),
]
INTEGRACOES = [
    ("Felipe Gurgel",     "Back Integrações ★",  "Felipe"),
    ("Keven Soares",      "Back Integrações ★",  "Keven"),
]
GESTAO = [
    ("Rafael Baena",      "Gestão Dev",          "Baena"),
    ("Laion Jordi",       "Produto",             "Laion"),
]

DAILY_QUERIES = [
    "Esteira Dev", "Esteira Dev Flat", "Esteira Dev Reprov",
    "Esteira Front End", "Esteira QA", "Esteira DevOps",
    "Integrações", "Espera Sprint", "Refinamento",
]

# ── Cores ─────────────────────────────────────────────────────────────────────
RS  = "\033[0m"
BD  = "\033[1m"
DM  = "\033[2m"
RE  = "\033[91m"
YE  = "\033[93m"
GR  = "\033[92m"
BL  = "\033[94m"
PU  = "\033[95m"
CY  = "\033[96m"
WH  = "\033[97m"
OR  = "\033[38;5;208m"   # laranja 2clix

def r(s):    return RE+str(s)+RS
def y(s):    return YE+str(s)+RS
def g(s):    return GR+str(s)+RS
def b(s):    return BL+str(s)+RS
def p(s):    return PU+str(s)+RS
def c(s):    return CY+str(s)+RS
def w(s):    return WH+str(s)+RS
def o(s):    return OR+str(s)+RS
def dim(s):  return DM+str(s)+RS
def bold(s): return BD+str(s)+RS


# ── Logo ──────────────────────────────────────────────────────────────────────
_LOGO = [
    r" ___    _ _     ",
    r"|_  )__| (_)_ __",
    r" / // _| | \ \ /",
    r"/___\__|_|_/_\_\\",
]

def print_logo(subtitle="Backlog Assistant · Plataforma Qualidade"):
    print()
    for idx, line in enumerate(_LOGO):
        dot = "  " + OR+BD+"●"+RS if idx == 0 else ""
        print("  " + WH+BD+line+RS + dot)
    print("  " + dim(subtitle))
    print()

# ── HTTP ──────────────────────────────────────────────────────────────────────
token = base64.b64encode((":" + PAT).encode()).decode()
BASE_ORG = ADO_HOST + "/" + ORG + "/_apis"

def base_for(project):
    return ADO_HOST + "/" + ORG + "/" + urllib.parse.quote(project) + "/_apis"

def ado_get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": "Basic " + token,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

def fetch_query(qid, project=None):
    base = base_for(project or PROJECT)
    data = ado_get(base + "/wit/wiql/" + qid + "?api-version=7.1")
    ids  = [wi["id"] for wi in data.get("workItems", [])][:200]
    if not ids:
        return []
    id_str = ",".join(str(i) for i in ids)
    data2  = ado_get(BASE_ORG + "/wit/workitems?ids=" + id_str + "&fields=" + FIELDS + "&api-version=7.1")
    result = []
    for wi in data2.get("value", []):
        f = wi["fields"]
        assigned = f.get("System.AssignedTo", {})
        if isinstance(assigned, dict):
            assigned = assigned.get("displayName", "Não atribuído")
        result.append({
            "id":          wi["id"],
            "title":       f.get("System.Title", ""),
            "state":       f.get("System.State", ""),
            "assignedTo":  (assigned or "Não atribuído").split(" <")[0].strip(),
            "priority":    str(f.get("Microsoft.VSTS.Common.Priority", "")),
            "type":        f.get("System.WorkItemType", ""),
            "changedDate": f.get("System.ChangedDate", ""),
            "createdDate": f.get("System.CreatedDate", ""),
            "effort":      f.get("Microsoft.VSTS.Scheduling.Effort", ""),
            "tags":        f.get("System.Tags", ""),
        })
    return result

def load_all():
    print("\n" + dim("Carregando queries do Azure DevOps..."))
    all_data = {}
    for name, (qid, proj) in QUERIES.items():
        try:
            items = fetch_query(qid, proj)
            all_data[name] = items
            print("  " + g("✓") + " " + name + ": " + str(len(items)) + " items")
        except Exception as e:
            print("  " + r("✗") + " " + name + ": " + str(e))
            all_data[name] = []
    return all_data

# ── Utils ─────────────────────────────────────────────────────────────────────
def days_since(ds):
    if not ds:
        return None
    try:
        dt = datetime.fromisoformat(ds.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except:
        return None

def fmt_date(ds):
    if not ds:
        return "—"
    try:
        return datetime.fromisoformat(ds.replace("Z", "+00:00")).strftime("%d/%m/%Y")
    except:
        return "?"

def age_str(d):
    if d is None: return ""
    if d > 5:     return r(str(d) + "d")
    if d > 2:     return y(str(d) + "d")
    return dim(str(d) + "d")

def pc(pri):
    if pri in ("0","1"): return RE
    if pri == "2":       return YE
    return DM

def sc(state):
    sl = (state or "").lower()
    if "reprovado" in sl or "bloqueado" in sl: return RE
    if "done" in sl or "publicado" in sl or "validado" in sl: return GR
    if "andamento" in sl or "executar" in sl: return BL
    if "qa" in sl: return CY
    if "sprint" in sl or "espera" in sl: return PU
    return WH

def bar(n, total, width=20):
    filled = int((n / max(total,1)) * width)
    col    = RE if n > 8 else YE if n > 4 else GR
    return col + "█"*filled + RS + DM + "░"*(width-filled) + RS

def section(title, col=WH, sub=""):
    s = ("  " + dim(sub)) if sub else ""
    print("\n" + DM + "─"*50 + RS)
    print(BD + col + "  " + title + RS + s)
    print(DM + "─"*50 + RS + "\n")

def print_item(item, maxw=50):
    iid   = item["id"]
    pri   = item["priority"]
    state = item["state"]
    title = item["title"]
    who   = item["assignedTo"]
    d     = days_since(item["changedDate"])
    print("  " + dim("#"+str(iid)+"  ") +
          pc(pri)+"P"+pri+RS + "  " +
          sc(state)+state[:22]+RS + "  " +
          age_str(d) + "  " +
          WH+title[:maxw]+RS + "  " +
          dim(who))

def find_items(flat, frag):
    return [i for i in flat if frag.lower() in i["assignedTo"].lower()]

def is_blocked(i):
    return any(k in i["state"].lower() for k in ["reprovado","bloqueado","duplicado"])

def is_done(i):
    return any(k in i["state"].lower() for k in ["done","publicado","validado qa","pronto para qa"])

def is_active(i):
    return any(k in i["state"].lower() for k in ["andamento","executar","fazendo"])

# ── Comandos ──────────────────────────────────────────────────────────────────
def cmd_resumo(data):
    flat = [i for v in data.values() for i in v]
    print_logo("Resumo Geral · Plataforma Qualidade")
    section("RESUMO GERAL — Plataforma Qualidade", WH)
    states = Counter(i["state"] for i in flat)
    print(bold("Por estado:"))
    for state, count in states.most_common(12):
        print("  " + sc(state)+state[:28]+RS + "  " + bold(str(count)) + "  " + dim(bar(count, len(flat), 15)))
    print("\n" + bold("Por query:"))
    for name, items in data.items():
        done = sum(1 for i in items if is_done(i))
        blk  = sum(1 for i in items if is_blocked(i))
        print("  " + c(name[:20]) + "  " + w(str(len(items))) + " items  " +
              g(str(done)) + " entregues  " +
              (r(str(blk)) if blk else dim("0")) + " bloqueados")
    print()

def cmd_daily(data):
    # Usa apenas as queries relevantes para a daily
    daily_flat = []
    for qname in DAILY_QUERIES:
        daily_flat.extend(data.get(qname, []))
    # Deduplica por ID (um item pode aparecer em mais de uma query)
    seen = set()
    flat = []
    for i in daily_flat:
        if i["id"] not in seen:
            seen.add(i["id"])
            flat.append(i)
    now  = datetime.now().strftime("%d/%m/%Y %H:%M")
    print_logo("Daily · " + now)
    print("\n" + PU+BD+"═"*50+RS)
    print(PU+BD+"  DAILY — " + now + RS)
    print(PU+BD+"═"*50+RS)
    print(dim("  Foco nos itens da Sprint e riscos de entrega."))
    print(dim("  Sem detalhamento técnico.\n"))
    print(dim("  Script: O que finalizei? / O que vou finalizar? / O que pode me impedir?\n"))

    def dev_block(label, role, frag, col=BL):
        items   = find_items(flat, frag)
        done_it = [i for i in items if is_done(i)]
        active  = [i for i in items if is_active(i)]
        blocked = [i for i in items if is_blocked(i)]
        stale   = [i for i in active if (days_since(i["changedDate"]) or 0) > 2]
        print(BD+col+"▶ "+label+RS + "  " + dim(role))
        if not items:
            print("  " + dim("Sem items ativos nas queries carregadas") + "\n")
            return
        if done_it:
            print("  " + g("✅ Finalizados (" + str(len(done_it)) + "):"))
            for i in done_it[:3]:
                iid = i["id"]
                print("     " + dim("#"+str(iid)) + "  " + i["title"][:55] + "  " + dim("["+i["state"]+"]"))
        if active:
            print("  " + b("🔨 Em andamento (" + str(len(active)) + "):"))
            for i in active[:4]:
                iid = i["id"]
                d   = days_since(i["changedDate"])
                sfx = "  " + y("⏱"+str(d)+"d") if d and d > 2 else ""
                print("     " + dim("#"+str(iid)) + "  " + i["title"][:55] + sfx)
        if blocked:
            print("  " + r("🔴 Reprovado/Bloqueado (" + str(len(blocked)) + "):"))
            for i in blocked:
                iid = i["id"]
                print("     " + dim("#"+str(iid)) + "  " + r(i["title"][:55]))
        if stale and not blocked:
            print("  " + y("⚠  Sem movimento há +2 dias (" + str(len(stale)) + ") — risco:"))
            for i in stale:
                iid = i["id"]
                d   = days_since(i["changedDate"])
                print("     " + dim("#"+str(iid)) + "  " + i["title"][:52] + "  " + y("("+str(d)+"d)"))
        if not active and not done_it and not blocked:
            outros = [i for i in items if not is_active(i) and not is_done(i) and not is_blocked(i)]
            if outros:
                sts = ", ".join(set(i["state"] for i in outros[:3]))
                print("  " + dim("Outros (" + str(len(outros)) + "): " + sts))
        print()

    def qa_block():
        pronto = [i for i in flat if "pronto para qa" in i["state"].lower()]
        reprov = [i for i in flat if "reprovado" in i["state"].lower()]
        tada_items    = find_items(flat, "Tada")
        fernando_items = find_items(flat, "fernando")
        qa_items = {i["id"]: i for i in tada_items + fernando_items}

        print(BD+PU+"▶ Rodrigo Tada + Fernando Alucema"+RS + "  " + dim("QA"))
        print("  " + c("🧪 Pronto para testar hoje (" + str(len(pronto)) + "):"))
        for i in pronto[:8]:
            iid = i["id"]
            print("     " + dim("#"+str(iid)) + "  " + i["title"][:52] + "  " + dim(i["assignedTo"]))
        if not pronto:
            print("     " + dim("Nenhum item em Pronto para QA"))
        print("  " + r("🔴 Reprovados — vira bug (" + str(len(reprov)) + "):"))
        for i in reprov[:8]:
            iid = i["id"]
            print("     " + dim("#"+str(iid)) + "  " + r(i["title"][:52]) + "  " + dim(i["assignedTo"]))
        if not reprov:
            print("     " + g("Nenhum item reprovado agora ✓"))
        if qa_items:
            print("  " + y("📋 Items atribuídos ao time QA (" + str(len(qa_items)) + "):"))
            for i in qa_items.values():
                iid = i["id"]
                d   = days_since(i["changedDate"])
                print("     " + dim("#"+str(iid)) + "  " + i["state"][:20] + "  " + i["title"][:45] + "  " + age_str(d))
        print()

    section("DEVS", WH)
    for label, role, frag in DEVS:
        dev_block(label, role, frag, BL)
    section("QA", WH, "responde depois dos devs, não em paralelo")
    qa_block()
    section("INTEGRAÇÕES", WH)
    for label, role, frag in INTEGRACOES:
        dev_block(label, role, frag, GR)
    section("GESTÃO", WH)
    for label, role, frag in GESTAO:
        dev_block(label, role, frag, CY)

    criticos = [i for i in flat if i["priority"] in ("0","1")]
    parados  = [i for i in flat if (days_since(i["changedDate"]) or 0) > 5]
    if criticos or parados:
        section("⚡ ALERTAS FINAIS", RE)
        if criticos:
            print("  " + r("P0/P1 ativos (" + str(len(criticos)) + "):"))
            for i in criticos[:6]:
                iid = i["id"]
                print("     " + dim("#"+str(iid)) + "  " + r(i["title"][:52]) + "  " + dim(i["assignedTo"]))
        if parados:
            print("\n  " + y("Parados há +5 dias (" + str(len(parados)) + "):"))
            for i in sorted(parados, key=lambda x: days_since(x["changedDate"]) or 0, reverse=True)[:4]:
                iid = i["id"]
                d   = days_since(i["changedDate"])
                print("     " + r(str(d)+"d") + "  " + dim("#"+str(iid)) + "  " + i["title"][:50] + "  " + dim(i["assignedTo"]))
        print()

def cmd_jornal(data):
    items = data.get("Jornal", [])
    print_logo("Jornal de Demandas · Plataforma Qualidade")
    section("JORNAL DE DEMANDAS — " + datetime.now().strftime("%d/%m/%Y"), PU)
    print(bold("Plataforma Qualidade · Relatório Semanal\n"))
    by_state = defaultdict(list)
    for i in items:
        by_state[i["state"]].append(i)
    ORDER = [
        ("Done",            GR, "✅ Concluídos"),
        ("Publicado",       GR, "🚀 Publicados em produção"),
        ("Validado QA",     YE, "⏳ Validados — aguardando publicação"),
        ("Pronto para QA",  CY, "🧪 Prontos para QA"),
        ("Em andamento",    BL, "🔨 Em desenvolvimento"),
        ("Para executar",   PU, "▶  Para executar"),
        ("Espera Sprint",   PU, "📋 Espera sprint"),
        ("Reprovado",       RE, "🔴 Reprovados — retrabalho"),
        ("Refinamento",     CY, "🔍 Em refinamento"),
        ("Pendente Esforço",YE, "⚖  Pendente estimativa"),
    ]
    total_done = len(by_state.get("Done",[])) + len(by_state.get("Publicado",[]))
    mapped = set()
    for state, col, label in ORDER:
        group = by_state.get(state, [])
        if not group:
            continue
        mapped.add(state)
        print(BD+col+label+" ("+str(len(group))+")"+RS)
        for i in group:
            iid = i["id"]
            d   = days_since(i["changedDate"])
            print("  " + dim("#"+str(iid)+"  ") +
                  pc(i["priority"])+"P"+i["priority"]+RS + "  " +
                  WH+i["title"][:55]+RS + "  " +
                  dim(i["assignedTo"][:22]) + "  " + age_str(d))
        print()
    outros = {s: v for s, v in by_state.items() if s not in mapped and v}
    if outros:
        print(dim("Outros estados:"))
        for state, group in outros.items():
            print("  " + dim(state+": "+str(len(group))+" items"))
        print()
    wip = Counter(i["assignedTo"] for i in items)
    blk = sum(1 for i in items if is_blocked(i))
    print(PU+BD+"─"*50+RS)
    print(PU+BD+"  SUMÁRIO EXECUTIVO"+RS)
    print(PU+BD+"─"*50+RS)
    print("  Total no Jornal         " + bold(w(str(len(items)))))
    print("  Entregues (Done+Pub)    " + bold(g(str(total_done))))
    print("  Aguardando publicação   " + bold(y(str(len(by_state.get("Validado QA",[]))))))
    print("  Em desenvolvimento      " + bold(b(str(len(by_state.get("Em andamento",[]))))))
    print("  Reprovados              " + (bold(r(str(blk))) if blk else g("0")))
    print("\n  " + bold("Top assignees:"))
    for person, count in wip.most_common(5):
        col = RE if count > 10 else YE if count > 5 else GR
        print("    " + col+str(count).rjust(3)+RS + "  " + person)
    print()

def cmd_gargalos(data):
    flat = [i for v in data.values() for i in v]
    print_logo("Gargalos e Bloqueios · Plataforma Qualidade")
    section("GARGALOS E BLOQUEIOS", RE)
    wip = defaultdict(list)
    for i in flat:
        wip[i["assignedTo"]].append(i)
    max_wip = max(len(v) for v in wip.values()) if wip else 1
    print(bold(r("🔴 WIP por pessoa:")))
    for person, items in sorted(wip.items(), key=lambda x: -len(x[1]))[:8]:
        n   = len(items)
        col = RE if n > 8 else YE if n > 4 else GR
        print("  " + col+BD+str(n).rjust(3)+RS + "  " + WH+person[:26]+RS + "  " + bar(n, max_wip, 20))
    blocked = [i for i in flat if is_blocked(i)]
    print("\n" + bold(r("🚨 Bloqueados / Reprovados (" + str(len(blocked)) + "):")))
    if not blocked:
        print("  " + g("Nenhum item bloqueado agora. ✓"))
    else:
        for i in blocked:
            print_item(i)
    criticos = [i for i in flat if i["priority"] in ("0","1") and (days_since(i["changedDate"]) or 0) > 2]
    print("\n" + bold(y("⚡ P0/P1 parados há +2 dias (" + str(len(criticos)) + "):")))
    if not criticos:
        print("  " + g("Nenhum item crítico parado. ✓"))
    else:
        for i in sorted(criticos, key=lambda x: days_since(x["changedDate"]) or 0, reverse=True):
            print_item(i)
    print()

def cmd_wip(data):
    flat = [i for v in data.values() for i in v]
    print_logo("WIP por Pessoa · Plataforma Qualidade")
    wip  = defaultdict(list)
    for i in flat:
        wip[i["assignedTo"]].append(i)
    max_wip = max(len(v) for v in wip.values()) if wip else 1
    section("WIP POR PESSOA", WH)
    for person, items in sorted(wip.items(), key=lambda x: -len(x[1])):
        n      = len(items)
        col    = RE if n > 8 else YE if n > 4 else GR
        states = Counter(i["state"] for i in items)
        print("  " + BD+col+person+RS + "  " + col+str(n)+" items"+RS + "  " + dim(bar(n, max_wip, 18)))
        for state, count in states.most_common():
            print("    " + sc(state)+str(count)+"x "+state+RS)
        print()

def cmd_parados(data):
    flat    = [i for v in data.values() for i in v]
    print_logo("Items Parados · Plataforma Qualidade")
    parados = [(i, days_since(i["changedDate"])) for i in flat if (days_since(i["changedDate"]) or 0) > 3]
    parados.sort(key=lambda x: -(x[1] or 0))
    section("ITEMS PARADOS HÁ MAIS DE 3 DIAS (" + str(len(parados)) + ")", YE)
    for item, _ in parados:
        print_item(item)
    print()

def cmd_ask(data):
    lines = ["Dados do backlog 2clix — Plataforma Qualidade — " + datetime.now().strftime("%d/%m/%Y")]
    for qname, items in data.items():
        lines.append("\n=== " + qname.upper() + " (" + str(len(items)) + " items) ===")
        for i in items:
            d = days_since(i["changedDate"])
            lines.append(
                "[#" + str(i["id"]) + "] " + i["type"] +
                " | Estado: " + i["state"] +
                " | Assignee: " + i["assignedTo"] +
                " | P" + i["priority"] +
                " | Effort: " + str(i["effort"] or "?") +
                " | Última mudança: " + fmt_date(i["changedDate"]) + " (" + str(d) + "d)" +
                " | Título: " + i["title"]
            )
    context = "\n".join(lines)
    system  = (
        "Você é o assistente de backlog da 2clix, especializado em gestão de demandas no Azure DevOps.\n"
        "Responda sempre em português brasileiro, direto e operacional.\n"
        "Destaque gargalos, cite IDs (#número) e assignees.\n"
        "Para tempo parado, calcule com base na data de última mudança.\n"
        "Contexto atual:\n" + context
    )

    print_logo("Assistente de IA · Plataforma Qualidade")
    print("  " + PU+"─"*42+RS)
    print("  " + PU+"✦  Assistente de IA — linguagem natural"+RS)
    print("  " + PU+"─"*42+RS)
    print("  " + dim("Digite sua pergunta. sair para voltar ao menu.") + "\n")

    history = []
    while True:
        try:
            q = input(BL+BD+"Você:"+RS+"  ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if q.lower() in ("sair","exit","quit",""):
            break
        history.append({"role": "user", "content": q})
        payload = json.dumps({
            "model":      "claude-sonnet-4-6",
            "max_tokens": 1000,
            "system":     system,
            "messages":   history,
        }).encode()
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
                    "anthropic-version": "2023-06-01",
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                dr = json.loads(resp.read())
            reply = dr["content"][0]["text"]
            history.append({"role": "assistant", "content": reply})
            print("\n" + PU+BD+"Claude:"+RS + "  " + reply + "\n")
        except Exception as e:
            print(r("Erro ao chamar Claude: " + str(e)) + "\n")

# ── Menu ──────────────────────────────────────────────────────────────────────
MENU = {
    "1": ("resumo",   "Resumo geral",             cmd_resumo),
    "2": ("daily",    "Daily — pauta por dev",     cmd_daily),
    "3": ("jornal",   "Jornal de Demandas",        cmd_jornal),
    "4": ("gargalos", "Gargalos e bloqueios",      cmd_gargalos),
    "5": ("wip",      "WIP por pessoa",            cmd_wip),
    "6": ("parados",  "Items parados há +3 dias",  cmd_parados),
    "7": ("ask",      "Perguntar ao Claude  ✦ IA", cmd_ask),
}

def menu_interativo(data):
    while True:
        flat = [i for v in data.values() for i in v]
        blk  = sum(1 for i in flat if is_blocked(i))
        par  = sum(1 for i in flat if (days_since(i["changedDate"]) or 0) > 3)
        don  = sum(1 for i in flat if is_done(i))
        print_logo("Backlog Assistant · Plataforma Qualidade")
        print(PU+BD+"╔══════════════════════════════════════════╗"+RS)
        print(PU+BD+"║  2clix · Backlog Assistant               ║"+RS)
        print(PU+BD+"║  Plataforma Qualidade                    ║"+RS)
        print(PU+BD+"╚══════════════════════════════════════════╝"+RS)
        print("\n  " + w(str(len(flat))) + " items   " +
              (r("● "+str(blk)+" bloqueados") if blk else dim("0 bloqueados")) + "   " +
              (y("⏱ "+str(par)+" parados") if par else dim("0 parados")) + "   " +
              g("✓ "+str(don)+" entregues") + "\n")
        for k, (_, desc, _) in MENU.items():
            icon = PU+"✦"+RS+"  " if "Claude" in desc else "   "
            print("  " + c(k) + "." + icon + w(desc))
        print("\n  " + dim("r. recarregar     0. sair") + "\n")
        try:
            choice = input(BL+BD+"Escolha:"+RS+" ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n" + dim("Até logo!") + "\n")
            break
        if choice == "0":
            print("\n" + dim("Até logo!") + "\n")
            break
        elif choice == "r":
            data = load_all()
        elif choice in MENU:
            MENU[choice][2](data)
        else:
            print("  " + r("Opção inválida."))

# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cmd  = sys.argv[1].lower() if len(sys.argv) > 1 else None
    data = load_all()
    if cmd is None:
        menu_interativo(data)
    else:
        match = next((fn for _, (name, _, fn) in MENU.items() if name == cmd), None)
        if match:
            match(data)
        else:
            print(r("Comando inválido. Use: resumo | daily | jornal | gargalos | wip | parados | ask"))
