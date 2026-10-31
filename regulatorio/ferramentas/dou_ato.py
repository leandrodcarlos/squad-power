"""Abre um ato do DOU. Uso: python -I dou_ato.py <urlTitle ou URL completa> [--grep "palavra"] [--salvar f.txt]"""
import sys, subprocess, re, html, argparse
from pathlib import Path
from urllib.parse import urlparse
sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser(); ap.add_argument("slug"); ap.add_argument("--grep", action="append", default=[])
ap.add_argument("--salvar"); ap.add_argument("--ctx", type=int, default=400)
a = ap.parse_args()
url = a.slug if a.slug.startswith("http") else "https://www.in.gov.br/web/dou/-/" + a.slug
host = urlparse(url).hostname or ""
if urlparse(url).scheme != "https" or not (host == "in.gov.br" or host.endswith(".in.gov.br")):
    sys.exit("Erro: só aceito endereço https do DOU (www.in.gov.br).")
if a.salvar and (Path(a.salvar).name != a.salvar or not a.salvar.lower().endswith(".txt")):
    sys.exit("Erro: --salvar aceita só um nome de arquivo .txt, gravado na pasta atual.")
raw = subprocess.run(["curl", "-s", "-L", "--proto", "=https", "--proto-redir", "=https", "-m", "90", "-A", "Mozilla/5.0", url], capture_output=True).stdout.decode("utf-8", "ignore")
m = re.search(r'<div class="texto-dou">(.*?)<div class="(?:informacao-conteudo|botoes)', raw, re.S)
body = m.group(1) if m else raw
pub = re.search(r"Publicado em:.*?</span>", raw, re.S)
t = re.sub(r"<script.*?</script>|<style.*?</style>", "", body, flags=re.S)
t = re.sub(r"<br\s*/?>|</p>|</div>|</tr>", "\n", t)
t = html.unescape(re.sub(r"<[^>]+>", " ", t)); t = re.sub(r"[ \t\r]+", " ", t); t = re.sub(r"\n\s*\n+", "\n", t)
print("URL:", url); print(html.unescape(re.sub(r"<[^>]+>", " ", pub.group(0))) if pub else "data de publicação não lida")
print("TAMANHO:", len(t)); print(t[:1500])
rev = re.findall(r"[^.\n]{0,160}(?:[Rr]evoga|[Ff]icam revogad|[Aa]ltera )[^.\n]{0,200}", t)
print("\nTRECHOS DE REVOGAÇÃO/ALTERAÇÃO:"); [print(" -", r.strip()) for r in rev[:15]]
for g in a.grep:
    print(f"\n=== GREP '{g}' ===")
    for mm in list(re.finditer(re.escape(g), t, re.I))[:8]:
        print("...", t[max(0, mm.start() - a.ctx):mm.end() + a.ctx].replace("\n", " "), "...\n")
if a.salvar: open(a.salvar, "w", encoding="utf-8").write(url + "\n" + t)
