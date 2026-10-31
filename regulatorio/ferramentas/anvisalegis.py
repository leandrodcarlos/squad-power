"""Abre um ato no AnvisaLegis e mostra status + trecho.
Uso: python -I anvisalegis.py TIPO NUMERO ANO [--grep "palavra"] [--salvar arquivo.txt]
TIPO: RDC | IN | POR | RES. Tenta automaticamente combinações de seqAto/orgao.
"""
import sys, subprocess, re, html, argparse
sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser()
ap.add_argument("tipo"); ap.add_argument("numero", type=int); ap.add_argument("ano")
ap.add_argument("--grep", action="append", default=[]); ap.add_argument("--salvar")
ap.add_argument("--ctx", type=int, default=400)
a = ap.parse_args()
TIPOS = {"RDC": ["RDC", "RES"], "IN": ["INM"], "INM": ["INM"], "POR": ["POR"], "RES": ["RES", "RDC"]}
ORGAOS = ["RDC/DC/ANVISA/MS", "DC/ANVISA/MS", "ANVISA/MS", "SVS/MS", "RDC/ANVS", "INMETRO/ME", "GM/MS"]
BASE = ("https://anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=detalharAto&valorAno={ano}"
        "&numeroAto={num:08d}&seqAto={seq}&tipo={tipo}&orgao={orgao}&codTipo=&desItem=&desItemFim="
        "&cod_menu=1696&cod_modulo=134&pesquisa=")
def limpa(raw):
    t = raw.decode("latin1", "ignore")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</div>|</tr>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"[ \t\r]+", " ", t); return re.sub(r"\n\s*\n+", "\n", t)
achou = None
for tipo in TIPOS.get(a.tipo.upper(), [a.tipo.upper()]):
    for seq in ["000", "002", "001"]:
        for org in ORGAOS:
            url = BASE.format(ano=a.ano, num=a.numero, seq=seq, tipo=tipo, orgao=org)
            r = subprocess.run(["curl", "-s", "-L", "-m", "60", "-A", "Mozilla/5.0", url], capture_output=True)
            t = limpa(r.stdout)
            if len(t) > 3000 and "está sendo processado" not in t[:2000]:
                achou = (url, t); break
        if achou: break
    if achou: break
if not achou:
    print("NAO_ENCONTRADO no AnvisaLegis (todas as combinações). Buscar no DOU."); sys.exit(1)
url, t = achou
print("URL:", url)
m = re.search(r"(INSTRU[ÇC][ÃA]O NORMATIVA|RESOLU[ÇC][ÃA]O|PORTARIA)[^\n]{0,200}", t)
ini = m.start() if m else 0
cab = t[max(0, ini - 600):ini + 600]
st = re.findall(r"(Vigente com Altera[çc][õo]es|Vigente|Revogad[oa][^\n]{0,120})", cab)
print("STATUS (cabeçalho):", st[:3] if st else "não identificado - ler cabeçalho abaixo")
print("CABEÇALHO:\n", cab.strip()[:1200])
alts = sorted(set(re.findall(r"\((?:Revogad[oa]|Reda[çc][ãa]o dada|Inclu[íi]d[oa])[^)]{0,120}\)", t)))
print("\nNOTAS DE ALTERAÇÃO/REVOGAÇÃO NO TEXTO (%d):" % len(alts))
for x in alts[:40]: print(" -", x)
for g in a.grep:
    print(f"\n=== GREP '{g}' ===")
    for mm in list(re.finditer(re.escape(g), t, re.I))[:8]:
        print("...", t[max(0, mm.start() - a.ctx):mm.end() + a.ctx].replace("\n", " "), "...\n")
if a.salvar:
    open(a.salvar, "w", encoding="utf-8").write(url + "\n" + t); print("salvo em", a.salvar)
