#!/usr/bin/env python
"""Gera o relatório de visita/auditoria (.docx), a mensagem de WhatsApp (.txt)
e a lista de conferência da consultora (.txt) a partir de um JSON.

Uso:
    python gerar_relatorio.py visita.json [--saida PASTA] [--nome NOME]

Schema do JSON: ver SKILL.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
except ImportError:
    print("Falta instalar o python-docx. Rode: python -m pip install python-docx", file=sys.stderr)
    sys.exit(1)

ALERTA = "⚠️"
RISCOS = ("alto", "medio", "baixo")
ROTULO = {"alto": "Alto", "medio": "Médio", "baixo": "Baixo"}
COR_RISCO = {"alto": "F4C7C3", "medio": "FCE8B2", "baixo": "CDE8D0"}
COR_TITULO = RGBColor(0x1F, 0x4E, 0x3D)
COR_CABECALHO = "1F4E3D"
FOTO_LARGURA_CM = 3.9
SEM_PRAZO = 9999
FOTO_EXTENSOES = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff"}

_SINONIMOS_RISCO = {"alta": "alto", "media": "medio", "baixa": "baixo"}


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _txt(v: Any) -> str:
    return "" if v is None else str(v).strip()


# ---------------------------------------------------------------- dados

def normalizar(dados: dict) -> dict:
    """Valida e devolve uma cópia normalizada (códigos NC, risco, status)."""
    for campo in ("cliente", "data"):
        if not _txt(dados.get(campo)):
            raise ValueError(f"Campo obrigatório ausente: {campo}")
    tipo = _sem_acento(_txt(dados.get("tipo") or "visita")).lower()
    if tipo not in ("visita", "auditoria"):
        raise ValueError("Campo tipo deve ser 'visita' ou 'auditoria'")
    itens = []
    for n, bruto in enumerate(dados.get("itens") or [], start=1):
        risco = _sem_acento(_txt(bruto.get("risco"))).lower()
        risco = _SINONIMOS_RISCO.get(risco, risco)
        if risco not in RISCOS:
            raise ValueError(f"NC{n:02d}: risco deve ser alto, medio ou baixo (recebido: {bruto.get('risco')!r})")
        status = _sem_acento(_txt(bruto.get("referencia_status"))).lower()
        referencia = _txt(bruto.get("referencia"))
        # só vale como conferida se veio da consulta ao vivo E há referência escrita
        status = "conferida" if (status == "conferida" and referencia) else "a conferir"
        itens.append({
            "codigo": f"NC{n:02d}",
            "area": _txt(bruto.get("area")),
            "achado": _txt(bruto.get("achado")),
            "evidencia_foto": bruto.get("evidencia_foto") or "",
            "risco": risco,
            "referencia": referencia,
            "referencia_status": status,
            "acao": _txt(bruto.get("acao")),
            "responsavel": _txt(bruto.get("responsavel")),
            "prazo": _txt(bruto.get("prazo")),
            "impacto": _txt(bruto.get("impacto")),
        })
    return {
        "cliente": _txt(dados["cliente"]),
        "data": _txt(dados["data"]),
        "consultora": _txt(dados.get("consultora")),
        "contato": _txt(dados.get("contato")),
        "tipo": tipo,
        "itens": itens,
        "pontos_positivos": [_txt(p) for p in dados.get("pontos_positivos") or [] if _txt(p)],
        "observacoes": _txt(dados.get("observacoes")),
    }


def _data_visita(data: str) -> date | None:
    try:
        return datetime.strptime(data, "%d/%m/%Y").date()
    except ValueError:
        return None


def prazo_em_dias(prazo: str, data_visita: str) -> int:
    p = _sem_acento(prazo).lower()
    if re.search(r"imediat|hoje|na hora|no ato", p):
        return 0
    m = re.search(r"(\d+)\s*(dia|semana|mes)", p)
    if m:
        return int(m.group(1)) * {"dia": 1, "semana": 7, "mes": 30}[m.group(2)]
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", p)
    base = _data_visita(data_visita)
    if m and base:
        try:
            return (date(int(m.group(3)), int(m.group(2)), int(m.group(1))) - base).days
        except ValueError:
            pass
    return SEM_PRAZO


def ordenar_plano(itens: list[dict], data_visita: str) -> list[dict]:
    ordem = {r: i for i, r in enumerate(RISCOS)}
    indexados = list(enumerate(itens))
    indexados.sort(key=lambda t: (ordem[t[1]["risco"]], prazo_em_dias(t[1]["prazo"], data_visita), t[0]))
    return [i for _, i in indexados]


def numeros(texto: str) -> list[str]:
    return re.findall(r"\d+(?:[.,]\d+)?", texto)


def contagem(itens: list[dict]) -> dict:
    return {r: sum(1 for i in itens if i["risco"] == r) for r in RISCOS}


# ---------------------------------------------------------------- docx helpers

def _sombra(celula, hex_cor: str) -> None:
    tc_pr = celula._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_cor)
    tc_pr.append(shd)


def _run(par, texto, negrito=False, cor=None, tamanho=None, italico=False):
    r = par.add_run(texto)
    r.bold, r.italic = negrito, italico
    if cor is not None:
        r.font.color.rgb = cor
    if tamanho:
        r.font.size = Pt(tamanho)
    return r


def _celula(celula, texto="", negrito=False, alerta="", tamanho=9):
    celula.text = ""
    par = celula.paragraphs[0]
    par.paragraph_format.space_after = Pt(2)
    _run(par, texto, negrito=negrito, tamanho=tamanho)
    if alerta:
        p2 = celula.add_paragraph()
        p2.paragraph_format.space_after = Pt(0)
        _run(p2, alerta, negrito=True, cor=RGBColor(0xB0, 0x3A, 0x00), tamanho=8)


def _tabela(doc, cabecalho: list[str], larguras_cm: list[float]):
    t = doc.add_table(rows=1, cols=len(cabecalho))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, (texto, larg) in enumerate(zip(cabecalho, larguras_cm)):
        c = t.rows[0].cells[i]
        c.width = Cm(larg)
        c.text = ""
        _run(c.paragraphs[0], texto, negrito=True, cor=RGBColor(0xFF, 0xFF, 0xFF), tamanho=9)
        _sombra(c, COR_CABECALHO)
    return t


def _linha(tabela, larguras_cm):
    row = tabela.add_row()
    for c, larg in zip(row.cells, larguras_cm):
        c.width = Cm(larg)
    return row


def _titulo(doc, texto, nivel=1):
    h = doc.add_heading(texto, level=nivel)
    for r in h.runs:
        r.font.color.rgb = COR_TITULO
        r.font.name = "Calibri"
    return h


def _par(doc, texto="", negrito=False, italico=False, tamanho=None, alinhamento=None):
    p = doc.add_paragraph()
    _run(p, texto, negrito=negrito, italico=italico, tamanho=tamanho)
    if alinhamento:
        p.alignment = alinhamento
    return p


def _alerta_numeros(*campos: str) -> str:
    nums = [n for c in campos for n in numeros(c)]
    return f"{ALERTA} conferir número: {', '.join(nums)}" if nums else ""


def _caminho_foto(valor) -> str:
    if isinstance(valor, (list, tuple)):
        return _txt(valor[0]) if valor else ""
    return _txt(valor).strip("\"'")


def _achar_foto(caminho: str, base: Path | None) -> Path:
    """Caminho relativo vale a partir da pasta atual ou, se não achar, da pasta do JSON."""
    p = Path(caminho)
    if p.is_absolute() or base is None or p.is_file():
        return p
    return base / p


# ---------------------------------------------------------------- documento

def _rotulos(d: dict) -> tuple[str, str]:
    if d["tipo"] == "auditoria":
        return "Relatório de Auditoria", "relatório de auditoria"
    return "Relatório de Visita Técnica", "relatório de visita"


def _capa(doc, d, titulo):
    for _ in range(6):
        doc.add_paragraph()
    _par(doc, titulo, negrito=True, tamanho=26, alinhamento=WD_ALIGN_PARAGRAPH.CENTER).runs[0].font.color.rgb = COR_TITULO
    _par(doc, d["cliente"], negrito=True, tamanho=18, alinhamento=WD_ALIGN_PARAGRAPH.CENTER)
    _par(doc, f"Data: {d['data']}", tamanho=12, alinhamento=WD_ALIGN_PARAGRAPH.CENTER)
    if d["consultora"]:
        _par(doc, f"Consultora responsável: {d['consultora']}", tamanho=12, alinhamento=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_page_break()


def _resumo(doc, d, pendencias: int):
    _titulo(doc, "Resumo executivo")
    itens, c = d["itens"], contagem(d["itens"])
    if d["pontos_positivos"]:
        _par(doc, "Pontos positivos", negrito=True)
        for p in d["pontos_positivos"]:
            doc.add_paragraph(p, style="List Bullet")
    if not itens:
        _par(doc, "Nenhuma não conformidade registrada nesta visita.")
    else:
        _par(doc, f"Foram registradas {len(itens)} não conformidades, por nível de risco:")
        for r in RISCOS:
            _par(doc, f"{ROTULO[r]}: {c[r]} não conformidade(s)")
    if d["observacoes"]:
        _par(doc, "Observações", negrito=True)
        _par(doc, d["observacoes"])
    if pendencias:
        _par(doc, f"{ALERTA} Há {pendencias} ponto(s) marcado(s) para conferência (números, referências, fotos) "
                  "antes de enviar ao cliente.", italico=True, tamanho=9)


def _tabela_ncs(doc, d, base=None):
    _titulo(doc, "Não conformidades")
    larg = [1.4, 6.0, 4.2, 1.8, 4.0]
    t = _tabela(doc, ["Cód.", "Área / achado", "Evidência", "Risco", "Referência"], larg)
    for i in d["itens"]:
        row = _linha(t, larg)
        _celula(row.cells[0], i["codigo"], negrito=True)
        achado = f"{i['area']}\n{i['achado']}" if i["area"] else i["achado"]
        if i["impacto"]:
            achado += f"\nImpacto: {i['impacto']}"
        _celula(row.cells[1], achado, alerta=_alerta_numeros(i["achado"], i["impacto"]))
        _evidencia(row.cells[2], i["evidencia_foto"], base)
        _celula(row.cells[3], ROTULO[i["risco"]], negrito=True)
        _sombra(row.cells[3], COR_RISCO[i["risco"]])
        _celula(row.cells[4], i["referencia"] or "—", alerta=_alerta_referencia(i))


def _alerta_referencia(i) -> str:
    return "" if i["referencia_status"] == "conferida" else f"{ALERTA} referência a conferir"


def _evidencia(celula, valor, base=None):
    caminho = _caminho_foto(valor)
    if not caminho:
        _celula(celula, "—")
        return
    p = _achar_foto(caminho, base)
    if not p.is_file():
        _celula(celula, "foto não localizada", alerta=f"{ALERTA} conferir arquivo")
        return
    celula.text = ""
    try:
        celula.paragraphs[0].add_run().add_picture(str(p), width=Cm(FOTO_LARGURA_CM))
    except Exception:  # imagem corrompida ou formato não suportado
        _celula(celula, "foto não pôde ser inserida", alerta=f"{ALERTA} conferir arquivo")


def _plano(doc, d):
    _titulo(doc, "Plano de ação")
    _par(doc, "Ordenado por risco e prazo. A coluna \"Feito?\" é para o cliente acompanhar.", italico=True, tamanho=9)
    larg = [1.4, 6.0, 3.0, 2.2, 1.6, 2.2]
    t = _tabela(doc, ["Cód.", "Ação corretiva", "Responsável", "Prazo", "Risco", "Feito?"], larg)
    for i in ordenar_plano(d["itens"], d["data"]):
        row = _linha(t, larg)
        _celula(row.cells[0], i["codigo"], negrito=True)
        _celula(row.cells[1], i["acao"] or "—", alerta=_alerta_numeros(i["acao"]))
        _celula(row.cells[2], i["responsavel"] or "—")
        _celula(row.cells[3], i["prazo"] or "—", alerta=_alerta_numeros(i["prazo"]))
        _celula(row.cells[4], ROTULO[i["risco"]], negrito=True)
        _sombra(row.cells[4], COR_RISCO[i["risco"]])
        _celula(row.cells[5], "")


def _mapeamento(doc, d):
    _titulo(doc, "Mapeamento de cláusulas (referência a conferir)")
    _par(doc, "As cláusulas abaixo são indicações de onde olhar. Confira o texto vigente da norma "
              "ou do esquema de certificação antes de citar ao cliente.", italico=True, tamanho=9)
    larg = [1.4, 11.0, 5.0]
    t = _tabela(doc, ["Cód.", "Requisito / cláusula", "Situação"], larg)
    for i in d["itens"]:
        row = _linha(t, larg)
        _celula(row.cells[0], i["codigo"], negrito=True)
        _celula(row.cells[1], i["referencia"] or "—")
        situacao = "conferida" if i["referencia_status"] == "conferida" else "referência a conferir"
        _celula(row.cells[2], situacao, alerta=_alerta_referencia(i))


def _rodape(doc, d, rotulo):
    p = doc.sections[-1].footer.paragraphs[0]
    p.text = ""
    _run(p, f"{d['cliente']} · {rotulo} · {d['data']}", tamanho=8)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def _propriedades(doc, d, titulo):
    cp = doc.core_properties
    autor = d["consultora"] or d["cliente"]
    cp.author = "" if autor.startswith("[") else autor
    cp.last_modified_by = cp.author
    cp.title = f"{titulo} - {d['cliente']}"
    cp.subject = cp.comments = cp.keywords = cp.category = ""


def montar_docx(d: dict, caminho: Path, pendencias: int, base: Path | None = None) -> None:
    titulo, rotulo = _rotulos(d)
    doc = Document()
    # Sem isso o Word mostra "python-docx" como autor nas propriedades do arquivo.
    doc.core_properties.author = ""
    doc.core_properties.comments = ""
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(1.8)
    sec.top_margin = sec.bottom_margin = Cm(2)
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(10.5)
    _capa(doc, d, titulo)
    _resumo(doc, d, pendencias)
    _tabela_ncs(doc, d, base)
    _plano(doc, d)
    if d["tipo"] == "auditoria":
        _mapeamento(doc, d)
    _rodape(doc, d, rotulo)
    _propriedades(doc, d, titulo)
    doc.save(str(caminho))


# ---------------------------------------------------------------- textos

def montar_whatsapp(d: dict) -> str:
    itens, c = d["itens"], contagem(d["itens"])
    nome = d["contato"]
    objeto = "auditoria" if d["tipo"] == "auditoria" else "visita"
    linhas = [f"Oi{', ' + nome if nome else ''}! Tudo bem?",
              f"Passando pra agradecer a {objeto} na {d['cliente']} ({d['data']})."]
    if d["pontos_positivos"]:
        linhas.append(f"Teve coisa boa por aí: {d['pontos_positivos'][0].rstrip('.')}.")
    if itens:
        prioridade = c["alto"]
        pontos = f"{len(itens)} ponto" + ("s" if len(itens) > 1 else "") + " de ajuste"
        linhas.append(f"Anotei {pontos}"
                      + (f", e {prioridade} pede atenção primeiro" if prioridade == 1 else
                         f", e {prioridade} pedem atenção primeiro" if prioridade > 1 else "")
                      + ". Já deixei tudo organizado no relatório, com plano de ação, responsável e prazo.")
        linhas.append("Podemos marcar uma conversa rápida pra eu te apresentar e alinharmos o que sai primeiro? "
                      "Depois te mando a versão final por e-mail, tá?")
    else:
        linhas.append("Não anotei pontos de ajuste desta vez, parabéns pelo capricho! "
                      "Te mando o relatório com o registro da visita.")
    linhas.append("Qualquer dúvida, me chama.")
    if d["consultora"]:
        linhas.append(d["consultora"])
    return "\n\n".join(linhas) + "\n"


def montar_revisao(d: dict, base: Path | None = None) -> tuple[str, int]:
    """Lista de conferência da consultora. Devolve (texto, nº de pontos)."""
    linhas = [f"CONFERIR ANTES DE ENVIAR - {d['cliente']} - {d['data']}", ""]
    pontos = 0
    nums, refs, fotos = [], [], []
    for i in d["itens"]:
        for rotulo, campo in (("achado", i["achado"]), ("impacto", i["impacto"]),
                              ("ação", i["acao"]), ("prazo", i["prazo"])):
            n = numeros(campo)
            if n:
                nums.append(f"- {i['codigo']} ({rotulo}): {', '.join(n)}  [\"{campo}\"]")
        if i["referencia_status"] != "conferida":
            refs.append(f"- {i['codigo']}: {i['referencia'] or '(sem referência)'}")
        caminho = _caminho_foto(i["evidencia_foto"])
        if caminho and Path(caminho).suffix.lower() not in FOTO_EXTENSOES:
            fotos.append(f"- {i['codigo']}: formato de foto não suportado ({caminho}); converta para JPG ou PNG")
        elif caminho and not _achar_foto(caminho, base).is_file():
            fotos.append(f"- {i['codigo']}: arquivo de foto não encontrado ({caminho})")
    blocos = [
        ("Números (temperatura, prazo, medida): confirme com a anotação da visita. "
         "Transcrição de áudio pode trocar \"9 graus\" por \"9º\" ou errar o número.", nums),
        ("Referências a conferir: use o agente regulatorio-fran (consulta ao vivo) ou o gov.br; "
         "não cite norma, artigo ou limite sem conferir.", refs),
        ("Fotos: arquivos não localizados ou em formato não suportado.", fotos),
    ]
    for titulo, lista in blocos:
        if lista:
            linhas += [titulo, *lista, ""]
            pontos += len(lista)
    if pontos == 0:
        linhas.append("Nada pendente de conferência automática. Faça a leitura final com o checklist da revisora.")
    linhas += ["", "Lembrete: remova os avisos de conferência do relatório depois de conferir, "
                   "e confirme que a mensagem não promete resultado em fiscalização."]
    return "\n".join(linhas) + "\n", pontos


# ---------------------------------------------------------------- principal

def gerar(dados: dict, saida: Path | str, nome: str = "relatorio", base: Path | None = None) -> dict:
    d = normalizar(dados)
    nome = Path(nome.replace("\\", "/")).name
    if nome in ("", ".", ".."):
        nome = "relatorio"
    pasta = Path(saida)
    pasta.mkdir(parents=True, exist_ok=True)
    texto_revisao, pendencias = montar_revisao(d, base)
    caminhos = {
        "docx": pasta / f"{nome}.docx",
        "whatsapp": pasta / "mensagem-whatsapp.txt",
        "revisao": pasta / "revisao-conferir.txt",
    }
    montar_docx(d, caminhos["docx"], pendencias, base)
    caminhos["whatsapp"].write_text(montar_whatsapp(d), encoding="utf-8")
    caminhos["revisao"].write_text(texto_revisao, encoding="utf-8")
    return caminhos


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Gera relatório de visita (.docx) e mensagem de WhatsApp.")
    ap.add_argument("json", help="arquivo JSON da visita")
    ap.add_argument("--saida", help="pasta de saída (padrão: pasta do JSON)")
    ap.add_argument("--nome", help="nome do .docx sem extensão (padrão: nome do JSON)")
    a = ap.parse_args(argv)
    origem = Path(a.json)
    try:
        dados = json.loads(origem.read_text(encoding="utf-8-sig"))
        saida = gerar(dados, a.saida or origem.parent, a.nome or origem.stem, origem.parent)
    except PermissionError:
        print("Erro: não consegui salvar. Feche o arquivo no Word e rode de novo.", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Erro: o arquivo JSON está inválido (linha {e.lineno}, coluna {e.colno}): {e.msg}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print("Erro: não consegui ler o arquivo. Salve o JSON como UTF-8.", file=sys.stderr)
        return 1
    except (OSError, ValueError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    for k, v in saida.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
