#!/usr/bin/env python3
"""Imprime o texto de um .docx, com tabelas, para revisão. Uso: python ler_docx.py arquivo.docx"""
import sys
from pathlib import Path


def ler(caminho: Path) -> str:
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(str(caminho))
    linhas = []
    for bloco in doc.iter_inner_content():
        if isinstance(bloco, Paragraph):
            if bloco.text.strip():
                linhas.append(bloco.text)
        elif isinstance(bloco, Table):
            for linha in bloco.rows:
                linhas.append(" | ".join(c.text.strip().replace("\n", " ") for c in linha.cells))
    return "\n".join(linhas)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        print("Uso: python ler_docx.py arquivo.docx", file=sys.stderr)
        return 2
    caminho = Path(sys.argv[1])
    if caminho.suffix.lower() != ".docx" or not caminho.is_file():
        print(f"Arquivo .docx não encontrado: {caminho}", file=sys.stderr)
        return 1
    try:
        print(ler(caminho))
    except ImportError:
        print("Falta a biblioteca. Rode: python -m pip install python-docx", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
