"""Busca no DOU (in.gov.br). Uso: python -I dou_busca.py "frase exata" [--recente] [--n 20]
Mostra data | título | link do ato | início do texto. Use frase do título/ementa ou "revoga a Resolução".
"""
import sys, subprocess, json, urllib.parse, argparse, re
sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser(); ap.add_argument("q"); ap.add_argument("--recente", action="store_true")
ap.add_argument("--n", type=int, default=20); ap.add_argument("--sem-aspas", action="store_true")
a = ap.parse_args()
q = a.q if a.sem_aspas else '"' + a.q + '"'
url = ("https://www.in.gov.br/consulta/-/buscar/dou?q=" + urllib.parse.quote(q) +
       f"&s=todos&exactDate=all&sortType={0 if a.recente else 1}&delta={a.n}")
raw = subprocess.run(["curl", "-s", "-L", "-m", "60", "-A", "Mozilla/5.0", url], capture_output=True).stdout.decode("utf-8", "ignore")
i = raw.find('"jsonArray":[')
if i < 0: print("SEM_RESULTADO/erro (bytes=%d)" % len(raw)); sys.exit(1)
seg = raw[i + 12:]; seg = seg[:seg.find("</script>")]; seg = seg[:seg.rfind("]") + 1]
try: arr = json.loads(seg)
except Exception: arr = json.loads(seg[:seg.rfind("}]") + 2])
print("BUSCA:", url, "| resultados:", len(arr))
for x in arr:
    print(x.get("pubDate"), "|", x.get("title"), "| https://www.in.gov.br/web/dou/-/" + str(x.get("urlTitle")),
          "|", re.sub(r"<[^>]+>", "", x.get("content") or "")[:250].replace("\n", " "))
