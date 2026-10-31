#!/usr/bin/env python
"""Gera documentos técnicos (POP, MBP, ficha técnica, PAC, planilhas) em .docx a partir de um JSON.

Uso:
    python gerar_documento.py entrada.json -o saida.docx

Regras embutidas (ver SKILL.md):
- números críticos (temperatura, tempo, concentração, %) saem com "⚠️ conferir" a menos que a
  seção traga "fonte_conferida" (consulta ao vivo feita via regulatorio-fran);
- referência a norma sem "conferir" no texto sai com "⚠️ referência a conferir";
- tabela nutricional de ficha técnica: só estrutura, valor preenchido é recusado;
- nenhuma marca de ferramenta/IA no arquivo (texto, rodapé ou propriedades).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

try:
    from docx import Document
    from docx.enum.section import WD_ORIENT
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor
except ImportError:
    print("Falta instalar o python-docx. Rode: python -m pip install python-docx", file=sys.stderr)
    sys.exit(1)

TIPOS = {"pop", "mbp", "ficha_tecnica", "pac", "planilha"}
FLAG = "⚠️"
FLAG_NUMERO = f" {FLAG} conferir"
FLAG_NORMA = f" {FLAG} referência a conferir"

RE_MARCA_IA_CS = re.compile(r"\bClaude\b|Anthropic|ChatGPT|OpenAI|\bIA\b|\bAI\b|inteligência artificial")
RE_NUMERO_CRITICO = re.compile(
    r"\d+(?:[.,]\d+)?\s*(?:°\s*C|º\s*C|graus|ppm|mg\s*/\s*[Ll]|g\s*/\s*[Ll]|%|"
    r"minutos?|min\b|horas?|h\b|segundos?|dias?\b|meses|ml\s*/\s*[Ll])",
    re.IGNORECASE,
)
RE_NORMA = re.compile(
    r"\b(?:RDC|IN|Portaria|Lei|Decreto|Resolução|Instrução Normativa)\s*(?:n[º°o.]*\s*)?\d+"
)
NOTA_NUTRICIONAL = (
    "Estrutura apenas. Os valores nutricionais devem ser calculados e conferidos por "
    "nutricionista (responsabilidade técnica do CRN)."
)


# ---------- cálculo de ficha técnica ----------
def _brl(v: float) -> str:
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_ficha(custo_total: float, rendimento_porcoes: float,
                   preco_venda: float | None = None) -> dict[str, Any]:
    """Custo por porção (e CMV/markup se houver preço) com a fórmula escrita."""
    if rendimento_porcoes <= 0:
        raise ValueError("Rendimento em porções precisa ser maior que zero.")
    custo_porcao = custo_total / rendimento_porcoes
    formula = (
        f"Custo por porção = custo total ÷ rendimento em porções = "
        f"R$ {_brl(custo_total)} ÷ {rendimento_porcoes:g} = R$ {_brl(custo_porcao)}"
    )
    out: dict[str, Any] = {"custo_porcao": custo_porcao, "formula": formula}
    if preco_venda:
        out["cmv"] = custo_porcao / preco_venda
        out["markup"] = preco_venda / custo_porcao if custo_porcao else None
        out["formula_cmv"] = (
            f"CMV = custo por porção ÷ preço de venda = R$ {_brl(custo_porcao)} ÷ "
            f"R$ {_brl(preco_venda)} = {out['cmv'] * 100:.1f}%".replace(".", ",")
        )
    return out


# ---------- validação ----------
def _varrer_textos(obj: Any):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _varrer_textos(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _varrer_textos(v)


def validar(dados: dict[str, Any]) -> None:
    for campo in ("tipo", "cliente", "titulo", "secoes"):
        if not dados.get(campo):
            raise ValueError(f"Campo obrigatório ausente: {campo}")
    if dados["tipo"] not in TIPOS:
        raise ValueError(f"tipo inválido: {dados['tipo']!r}. Use um de: {', '.join(sorted(TIPOS))}")
    for texto in _varrer_textos(dados):
        if RE_MARCA_IA_CS.search(texto):
            raise ValueError(f"Texto com marca de ferramenta/IA não é permitido: {texto[:60]!r}")
    for i, s in enumerate(dados["secoes"], 1):
        titulo = s.get("titulo")
        if not titulo:
            raise ValueError(f"Seção {i} sem título.")
        if not (s.get("conteudo") or s.get("itens") or s.get("tabela")):
            raise ValueError(f"Seção '{titulo}' sem conteúdo, itens ou tabela.")
        if dados["tipo"] == "ficha_tecnica" and _eh_nutricional(s):
            _checa_nutricional(s)


def _eh_nutricional(secao: dict[str, Any]) -> bool:
    return "nutricion" in secao.get("titulo", "").lower() and bool(secao.get("tabela"))


def _checa_nutricional(secao: dict[str, Any]) -> None:
    for linha in secao["tabela"].get("linhas", []):
        if any(str(c).strip() for c in linha[1:]):
            raise ValueError(
                "Tabela nutricional da ficha técnica é só estrutura: deixe os valores em branco "
                "(cálculo é do nutricionista)."
            )


# ---------- helpers de formatação ----------
def _marcar(texto: str, confirmado: bool, pendencias: list[str], secao: str) -> str:
    """Acrescenta flags de conferência e registra pendência."""
    if FLAG in texto:
        pendencias.append(f"{secao}: {texto[:140]}")
        return texto
    extra = ""
    if not confirmado:
        if RE_NORMA.search(texto) and "conferir" not in texto.lower():
            extra += FLAG_NORMA
        if RE_NUMERO_CRITICO.search(texto):
            extra += FLAG_NUMERO
    if extra:
        pendencias.append(f"{secao}: {texto[:140]}")
    return texto + extra


def _escreve(par, texto: str, negrito: bool = False, tamanho: float | None = None) -> None:
    antes, sep, depois = texto.partition(FLAG)
    if antes:
        r = par.add_run(antes)
        r.bold = negrito
        if tamanho:
            r.font.size = Pt(tamanho)
    if sep:
        r = par.add_run(sep + depois)
        r.bold = True
        r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        if tamanho:
            r.font.size = Pt(tamanho)


def _sombra(celula, cor: str) -> None:
    tc_pr = celula._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), cor)
    tc_pr.append(shd)


def _campo_pagina(par) -> None:
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    run = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "1"
    run.append(t)
    fld.append(run)
    par._p.append(fld)


def _repete_cabecalho(linha) -> None:
    tr_pr = linha._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


def _tabela(doc, spec: dict[str, Any], confirmado: bool, pendencias: list[str], secao: str,
            nutricional: bool) -> None:
    colunas = spec["colunas"]
    linhas = [list(map(str, l)) for l in spec.get("linhas", [])]
    vazias = int(spec.get("linhas_vazias", 0))
    t = doc.add_table(rows=1, cols=len(colunas))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, nome in enumerate(colunas):
        c = t.rows[0].cells[i]
        c.text = ""
        _escreve(c.paragraphs[0], nome, negrito=True, tamanho=10)
        _sombra(c, "D9D9D9")
    _repete_cabecalho(t.rows[0])
    for linha in linhas:
        cells = t.add_row().cells
        for i in range(len(colunas)):
            valor = linha[i] if i < len(linha) else ""
            if not nutricional:
                valor = _marcar(valor, confirmado, pendencias, secao)
            _escreve(cells[i].paragraphs[0], valor, tamanho=10)
    for _ in range(vazias):
        t.add_row()
    doc.add_paragraph()


def _cabecalho(doc, dados: dict[str, Any], data: str) -> None:
    sec = doc.sections[0]
    hdr = sec.header
    hdr.is_linked_to_previous = False
    tab = hdr.add_table(rows=2, cols=3, width=sec.page_width - sec.left_margin - sec.right_margin)
    tab.style = "Table Grid"
    valores = [
        [("Cliente", dados["cliente"]), ("Documento", dados["titulo"]), ("Código", dados.get("codigo", "-"))],
        [("Versão / data", f"{dados.get('versao', '1.0')} · {data}"),
         ("Elaborado por", dados.get("elaborado_por", "-")),
         ("Aprovado por", dados.get("aprovado_por", "-"))],
    ]
    for r, linha in enumerate(valores):
        for c, (rot, val) in enumerate(linha):
            cel = tab.rows[r].cells[c]
            cel.text = ""
            p = cel.paragraphs[0]
            run = p.add_run(f"{rot}: ")
            run.bold = True
            run.font.size = Pt(8.5)
            run2 = p.add_run(str(val))
            run2.font.size = Pt(8.5)
            _sombra(cel, "F2F2F2")


def _rodape(doc, dados: dict[str, Any], data: str) -> None:
    ftr = doc.sections[0].footer
    ftr.is_linked_to_previous = False
    p = ftr.paragraphs[0]
    p.text = f"{dados['cliente']} · {dados['titulo']} · Versão {dados.get('versao', '1.0')} · {data}"
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.size = Pt(8.5)
    p2 = ftr.add_paragraph("Página ")
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _campo_pagina(p2)
    for r in p2.runs:
        r.font.size = Pt(8.5)


def _assinaturas(doc, dados: dict[str, Any]) -> None:
    t = doc.add_table(rows=3, cols=3)
    t.style = "Table Grid"
    for i, h in enumerate(("Responsável", "Data", "Assinatura")):
        c = t.rows[0].cells[i]
        c.text = ""
        _escreve(c.paragraphs[0], h, negrito=True, tamanho=10)
        _sombra(c, "D9D9D9")
    t.rows[1].cells[0].text = f"Elaborado por: {dados.get('elaborado_por', '')}"
    t.rows[2].cells[0].text = f"Aprovado por: {dados.get('aprovado_por', '')}"


# ---------- geração ----------
def gerar(dados: dict[str, Any], saida: str | Path) -> Path:
    validar(dados)
    data = dados.get("data") or date.today().strftime("%d/%m/%Y")
    doc = Document()
    # Sem isso o Word mostra "python-docx" como autor nas propriedades do arquivo.
    doc.core_properties.author = ""
    doc.core_properties.comments = ""

    estilo = doc.styles["Normal"]
    estilo.font.name = "Calibri"
    estilo.font.size = Pt(11)
    h1 = doc.styles["Heading 1"]
    h1.font.name = "Calibri"
    h1.font.size = Pt(13)
    h1.font.color.rgb = RGBColor(0x1F, 0x3A, 0x2E)

    sec = doc.sections[0]
    if dados["tipo"] == "planilha":
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = sec.page_height, sec.page_width

    cp = doc.core_properties
    autor = dados.get("elaborado_por") or dados["cliente"]
    cp.author = "" if autor.startswith("[") else autor
    cp.last_modified_by = cp.author
    cp.title = dados["titulo"]
    cp.comments = ""
    cp.subject = dados["cliente"]

    _cabecalho(doc, dados, data)
    _rodape(doc, dados, data)

    titulo = doc.add_paragraph()
    r = titulo.add_run(dados["titulo"])
    r.bold = True
    r.font.size = Pt(16)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    pendencias: list[str] = [f"{FLAG} {f}" if FLAG not in f else f for f in dados.get("flags", [])]
    flags_explicitas = list(pendencias)
    pendencias = []

    for n, s in enumerate(dados["secoes"], 1):
        doc.add_heading(f"{n}. {s['titulo']}", level=1)
        confirmado = bool(s.get("fonte_conferida"))
        conteudo = s.get("conteudo") or []
        if isinstance(conteudo, str):
            conteudo = [conteudo]
        nutri = dados["tipo"] == "ficha_tecnica" and _eh_nutricional(s)
        for texto in conteudo:
            _escreve(doc.add_paragraph(), _marcar(texto, confirmado, pendencias, s["titulo"]))
        for item in s.get("itens", []):
            _escreve(doc.add_paragraph(style="List Bullet"),
                     _marcar(item, confirmado, pendencias, s["titulo"]))
        if s.get("tabela"):
            _tabela(doc, s["tabela"], confirmado, pendencias, s["titulo"], nutri)
            if nutri:
                nota = doc.add_paragraph()
                rr = nota.add_run(NOTA_NUTRICIONAL)
                rr.italic = True
                rr.font.size = Pt(9.5)
        if confirmado:
            nota = doc.add_paragraph()
            rr = nota.add_run(f"Fonte conferida: {s['fonte_conferida']}")
            rr.italic = True
            rr.font.size = Pt(9)

    if dados["tipo"] != "planilha":
        doc.add_heading("Elaboração e aprovação", level=1)
        _assinaturas(doc, dados)

    todas = flags_explicitas + pendencias
    if todas and dados.get("incluir_pendencias", True):
        doc.add_heading("Pendências para conferir (apagar esta página depois de conferir)", level=1)
        for p in todas:
            doc.add_paragraph(p, style="List Bullet 2")

    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(saida))
    return saida


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Gera documento técnico .docx a partir de JSON.")
    ap.add_argument("entrada", help="arquivo JSON")
    ap.add_argument("-o", "--saida", required=True, help="arquivo .docx de saída")
    args = ap.parse_args(argv)
    try:
        dados = json.loads(Path(args.entrada).read_text(encoding="utf-8-sig"))
        caminho = gerar(dados, args.saida)
    except PermissionError:
        print("Erro: não consegui salvar. Feche o arquivo no Word e rode de novo.", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Erro: o arquivo JSON está inválido (linha {e.lineno}, coluna {e.colno}): {e.msg}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print("Erro: não consegui ler o arquivo. Salve o JSON como UTF-8.", file=sys.stderr)
        return 1
    except (ValueError, OSError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    print(f"Gerado: {caminho}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
