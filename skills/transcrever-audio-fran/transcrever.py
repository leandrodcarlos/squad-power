"""Transcreve áudio/vídeo (visita técnica gravada no celular) para texto PT-BR, 100% local.

Uso: python transcrever.py <arquivo> [<arquivo>...] [--modelo medium] [--saida DIR] [--timestamps]

- GPU (CUDA, int8_float16, modelo "medium") quando disponível; senão CPU (int8, modelo "small").
- Áudio longo é fatiado em partes de 20 min (RAM estoura com áudio longo inteiro) e cada
  parte é guardada ao terminar: se cair no meio, rodar de novo retoma de onde parou.
- Saída: "<nome> - Transcrição.txt" ao lado do arquivo (ou em --saida), gravada de forma atômica.
"""
import argparse
import glob
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, Optional, Sequence

# DLLs CUDA vêm dos pacotes pip nvidia-cublas-cu12 / nvidia-cudnn-cu12 (fora do PATH).
# Precisa rodar antes de importar faster_whisper. Sem os pacotes, simplesmente não faz nada.
def _registrar_dlls_cuda() -> None:
    if not hasattr(os, "add_dll_directory"):
        return
    padrao = os.path.join(sys.prefix, "Lib", "site-packages", "nvidia", "*", "bin")
    for pasta in glob.glob(padrao):
        os.add_dll_directory(pasta)
        os.environ["PATH"] = pasta + os.pathsep + os.environ.get("PATH", "")


_registrar_dlls_cuda()

SEGUNDOS_POR_FATIA = 1200
MODELO_GPU = "medium"
MODELO_CPU = "small"
EXTENSOES = {".m4a", ".ogg", ".opus", ".mp3", ".wav", ".mp4", ".aac", ".webm", ".mkv", ".mov", ".flac", ".wma", ".amr"}

# Conservador: só siglas que o Whisper escreve em minúsculas. Palavra inteira, nada de prefixo.
GLOSSARIO = [
    (re.compile(r"\brdc\b", re.IGNORECASE), "RDC"),
    (re.compile(r"\banvisa\b", re.IGNORECASE), "ANVISA"),
    (re.compile(r"\bbpf\b", re.IGNORECASE), "BPF"),
    (re.compile(r"\bappcc\b", re.IGNORECASE), "APPCC"),
    (re.compile(r"\bpops\b", re.IGNORECASE), "POPs"),
    (re.compile(r"\bpop\b", re.IGNORECASE), "POP"),
]


FALTA_WHISPER = "faster-whisper não instalado. Rode: python -m pip install faster-whisper"


class ErroAmbiente(RuntimeError):
    """Problema do ambiente (ffmpeg ausente etc.), com mensagem pronta para o usuário."""


# ---------- texto ----------
def aplicar_glossario(texto: str) -> str:
    for padrao, certo in GLOSSARIO:
        texto = padrao.sub(certo, texto)
    return texto


def formatar_ts(segundos: float) -> str:
    total = int(segundos)
    return f"[{total // 60:02d}:{total % 60:02d}]"


def caminho_saida(arquivo: Path, pasta_saida: Optional[Path] = None) -> Path:
    return (pasta_saida or arquivo.parent) / f"{arquivo.stem} - Transcrição.txt"


def _escrever_atomico(destino: Path, texto: str) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_name(destino.name + ".part")
    tmp.write_text(texto, encoding="utf-8")
    os.replace(tmp, destino)


# ---------- ffmpeg ----------
def checar_ffmpeg() -> None:
    if not shutil.which("ffmpeg"):
        raise ErroAmbiente(
            "ffmpeg não encontrado. Instale e abra um terminal novo: "
            "no Windows rode 'winget install Gyan.FFmpeg'; no Mac 'brew install ffmpeg'."
        )


def fatiar_audio(arquivo: Path, pasta: Path) -> list[Path]:
    """Extrai o áudio em mp3 mono 16 kHz fatiado em 20 min. Reusa fatias já extraídas."""
    pasta.mkdir(parents=True, exist_ok=True)
    pronto = pasta / ".fatiado"
    if not pronto.exists():
        for velho in pasta.glob("parte_*.mp3"):
            velho.unlink()
        r = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(arquivo), "-vn", "-ac", "1", "-ar", "16000",
             "-b:a", "64k", "-f", "segment", "-segment_time", str(SEGUNDOS_POR_FATIA),
             str(pasta / "parte_%03d.mp3")],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg falhou: {r.stderr.strip()[-300:]}")
        pronto.write_text("ok", encoding="utf-8")
    partes = sorted(pasta.glob("parte_*.mp3"))
    if not partes:
        raise RuntimeError("ffmpeg não gerou fatias (arquivo sem áudio?)")
    return partes


# ---------- modelo ----------
def _fabrica_whisper(nome: str, device: str, compute_type: str):
    from faster_whisper import WhisperModel
    return WhisperModel(nome, device=device, compute_type=compute_type)


def carregar_modelo(modelo: Optional[str], fabrica: Callable = _fabrica_whisper,
                    forcar_cpu: bool = False):
    """Tenta GPU; se falhar, CPU. Devolve (modelo, 'cuda'|'cpu')."""
    if not forcar_cpu:
        try:
            return fabrica(modelo or MODELO_GPU, "cuda", "int8_float16"), "cuda"
        except ImportError:
            raise ErroAmbiente(FALTA_WHISPER)
        except Exception as e:  # sem GPU, driver ou DLL: cai para CPU
            print(f"GPU indisponível ({str(e)[:80]}). Usando CPU.", file=sys.stderr)
    nome = modelo or MODELO_CPU
    try:
        return fabrica(nome, "cpu", "int8"), "cpu"
    except ImportError:
        raise ErroAmbiente(FALTA_WHISPER)
    except Exception as e:
        raise ErroAmbiente(
            f"Não consegui carregar o modelo '{nome}'. Na primeira execução ele é baixado e precisa de "
            f"internet. Conecte e rode de novo. Detalhe: {str(e)[:120]}")


# ---------- transcrição ----------
def texto_da_fatia(parte: Path, modelo, timestamps: bool, offset: float) -> str:
    """Transcreve uma fatia; guarda o resultado ao lado (retomável)."""
    sufixo = ".ts.txt" if timestamps else ".txt"
    cache = parte.with_suffix(sufixo)
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    segmentos, _ = modelo.transcribe(str(parte), language="pt", vad_filter=True, beam_size=5)
    linhas = []
    for s in segmentos:
        txt = s.text.strip()
        if txt:
            prefixo = formatar_ts(offset + s.start) + " " if timestamps else ""
            linhas.append(prefixo + txt + "\n")
    texto = "".join(linhas)
    _escrever_atomico(cache, texto)
    return texto


def transcrever_arquivo(arquivo: Path, modelo, pasta_saida: Optional[Path], timestamps: bool,
                        fatiador: Callable = fatiar_audio, pasta_trabalho: Optional[Path] = None
                        ) -> Optional[Path]:
    """Devolve o caminho gravado, ou None se a transcrição veio vazia."""
    pasta = pasta_trabalho or _pasta_trabalho(arquivo)
    partes = fatiador(arquivo, pasta)
    texto = "".join(
        texto_da_fatia(p, modelo, timestamps, i * SEGUNDOS_POR_FATIA) for i, p in enumerate(partes))
    if not texto.strip():
        return None
    final = caminho_saida(arquivo, pasta_saida)
    _escrever_atomico(final, aplicar_glossario(texto))
    shutil.rmtree(pasta, ignore_errors=True)
    return final


def _pasta_trabalho(arquivo: Path, base: Optional[Path] = None) -> Path:
    base = base or Path(tempfile.gettempdir()) / "transcrever-audio-fran"
    limpo = re.sub(r"[^\w\-]+", "_", arquivo.stem).strip("_")[:60]
    return base / f"{limpo}_{hashlib.sha1(str(arquivo.resolve()).encode('utf-8')).hexdigest()[:8]}"


def processar(arquivos: Sequence[Path], modelo_nome: Optional[str], pasta_saida: Optional[Path],
              timestamps: bool, fabrica: Callable = _fabrica_whisper,
              fatiador: Callable = fatiar_audio, pasta_base: Optional[Path] = None
              ) -> list[Optional[Path]]:
    """Transcreve a fila. Erro de CUDA no meio (DLL, RAM): recarrega na CPU e refaz o arquivo."""
    modelo, device = carregar_modelo(modelo_nome, fabrica)
    print(f"Dispositivo: {device}")
    saidas: list[Optional[Path]] = []
    for arq in arquivos:
        pasta = _pasta_trabalho(arq, pasta_base)
        try:
            saidas.append(transcrever_arquivo(arq, modelo, pasta_saida, timestamps, fatiador, pasta))
        except Exception as e:
            if device != "cuda":
                print(f"ERRO em {arq.name}: {e}", file=sys.stderr)
                saidas.append(None)
                continue
            print(f"Falha na GPU ({str(e)[:80]}). Refazendo na CPU.", file=sys.stderr)
            modelo, device = carregar_modelo(modelo_nome, fabrica, forcar_cpu=True)
            try:
                saidas.append(transcrever_arquivo(arq, modelo, pasta_saida, timestamps, fatiador, pasta))
            except Exception as e2:
                print(f"ERRO em {arq.name}: {e2}", file=sys.stderr)
                saidas.append(None)
    return saidas


# ---------- CLI ----------
def _argumentos(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Transcreve áudio/vídeo para texto PT-BR (local).")
    ap.add_argument("arquivos", nargs="+", type=Path)
    ap.add_argument("--modelo", default=None, help="tiny/base/small/medium/large-v3 (padrão: medium na GPU, small na CPU)")
    ap.add_argument("--saida", type=Path, default=None, help="pasta de saída (padrão: ao lado do arquivo)")
    ap.add_argument("--timestamps", action="store_true", help="prefixa cada trecho com [mm:ss]")
    return ap.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None, checar: Callable = checar_ffmpeg,
         fabrica: Callable = _fabrica_whisper) -> int:
    args = _argumentos(argv)
    faltando = [a for a in args.arquivos if not a.is_file()]
    if faltando:
        for a in faltando:
            print(f"ERRO: arquivo não encontrado: {a}", file=sys.stderr)
        return 1
    try:
        checar()
    except ErroAmbiente as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    try:
        saidas = processar(args.arquivos, args.modelo, args.saida, args.timestamps, fabrica)
    except ErroAmbiente as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    for arq, saida in zip(args.arquivos, saidas):
        print(f"OK: {saida}" if saida else f"VAZIO/FALHA: {arq.name}")
    print("Revise termos técnicos e números de norma: o Whisper pode errar.")
    return 0 if all(saidas) else 2


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    sys.exit(main())
