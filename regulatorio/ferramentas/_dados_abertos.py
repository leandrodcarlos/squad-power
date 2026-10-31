"""Utilitarios comuns das consultas em dados abertos (Anvisa, MAPA). So biblioteca padrao.

Regras: 1 requisicao por vez, User-Agent identificado, cache em disco (padrao 24 h) para nao
baixar o CSV a cada pergunta. Sem login, sem contornar bloqueio: se der 401/403/captcha, falha e diz.
"""
import csv
import io
import json
import os
import re
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.request

UA = "squad-fran-regulatorio/1.0 (consulta publica de dados abertos)"
CACHE_DIR = os.environ.get("REGULATORIO_CACHE", os.path.join(tempfile.gettempdir(), "regulatorio-fran-cache"))
CACHE_HORAS = 24


class SemAcesso(Exception):
    """Fonte respondeu erro/bloqueio. Nao tentar contornar; documentar e orientar caminho manual."""


def baixar(url: str, nome_cache: str, horas: float = CACHE_HORAS, timeout: int = 120) -> bytes:
    os.makedirs(CACHE_DIR, exist_ok=True)
    caminho = os.path.join(CACHE_DIR, nome_cache)
    if os.path.exists(caminho) and time.time() - os.path.getmtime(caminho) < horas * 3600:
        with open(caminho, "rb") as f:
            return f.read()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            dados = r.read()
    except urllib.error.HTTPError as e:
        raise SemAcesso(f"HTTP {e.code} em {url}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise SemAcesso(f"falha de rede em {url}: {e}") from e
    with open(caminho, "wb") as f:
        f.write(dados)
    return dados


def json_de(url: str, nome_cache: str, horas: float = 6) -> dict:
    return json.loads(baixar(url, nome_cache, horas).decode("utf-8"))


def consertar(texto: str) -> str:
    """Desfaz UTF-8 lido como latin-1 ('RenovaÃ§Ã£o' vira 'Renovação'); se nao der, devolve igual."""
    if "Ã" in texto or "Â" in texto:
        for enc in ("cp1252", "latin-1"):
            try:
                return texto.encode(enc).decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
    return texto


def decodificar(dados: bytes) -> str:
    try:
        return dados.decode("utf-8-sig")
    except UnicodeDecodeError:
        return dados.decode("latin-1")


def linhas_csv(dados: bytes):
    """Gera dicts (delimitador ';'), valores com mojibake corrigido."""
    leitor = csv.DictReader(io.StringIO(decodificar(dados)), delimiter=";")
    for lin in leitor:
        yield {(k or "").strip(): consertar((v or "").strip()) for k, v in lin.items()}


def norm(texto: str) -> str:
    """Minusculas sem acento, para comparar."""
    t = unicodedata.normalize("NFKD", texto or "")
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c)).lower()).strip()


def contem(valor: str, termo: str) -> bool:
    """True se TODAS as palavras de `termo` aparecem em `valor` (sem acento, sem caixa)."""
    v = norm(valor)
    return all(p in v for p in norm(termo).split())


def so_digitos(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def sair_erro(msg: str, codigo: int = 2):
    print("SEM_ACESSO_PROGRAMATICO:", msg, file=sys.stderr)
    sys.exit(codigo)
