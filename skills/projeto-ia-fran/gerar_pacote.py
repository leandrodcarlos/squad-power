#!/usr/bin/env python3
"""Gera o pacote de um projeto de IA (Claude Projects / Gemini Gem / GPT) a partir de um JSON.

Uso:
    python gerar_pacote.py respostas.json [--saida PASTA]
    python gerar_pacote.py --validar PASTA

Escreve 6 arquivos: instrucoes.md, modelo-da-entrega.md, base-da-area.md,
exemplo-bom.md, teste.md, COMO-USAR.md.
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

LIMITE_INSTRUCOES = 8000  # limite do campo de instruções de um GPT
ARQUIVOS = ["instrucoes.md", "modelo-da-entrega.md", "base-da-area.md",
            "exemplo-bom.md", "teste.md", "COMO-USAR.md"]
CAMPOS_OBRIGATORIOS = ["titulo", "tarefa", "destinatario", "objetivo", "entradas",
                       "passos", "modelo_secoes", "referencias", "exemplo_bom", "testes"]

NUNCA_PADRAO = [
    "Inventar número de norma, artigo, limite, temperatura, prazo legal ou valor de referência. "
    "Se não tiver certeza, escreva `[conferir: o que conferir e onde]` e siga.",
    "Garantir aprovação em fiscalização, licença ou auditoria. Fale em \"reduz risco\" e \"deixa preparado\".",
    "Repetir CNPJ, CPF, telefone, e-mail ou nome de pessoa do cliente final. Use [CLIENTE] e [EMPRESA].",
    "Inventar dado que eu não enviei. Se faltar informação, escreva `[FALTA INFORMAR: ...]` e pergunte no fim.",
    "Mudar a ordem ou os títulos do modelo da entrega.",
]

RE_CNPJ = re.compile(r"\b[0-9A-Z]{2}\.?[0-9A-Z]{3}\.?[0-9A-Z]{3}/?[0-9A-Z]{4}-?\d{2}\b")
RE_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RE_FONE = re.compile(
    r"(?<![\w/])(?!(?:19|20)\d{2}[-.\s](?:19|20)\d{2}\b)"
    r"(?:(?:\+?55\s?)?\(?\d{2}\)?[\s.-]?9?[\s.-]?\d{4}[-.\s]?\d{4}|9?\d{4}[-.\s]\d{4})\b")


def anonimizar(texto, nomes=()):
    """Remove CNPJ, CPF, e-mail, telefone e os nomes informados. Não muta a entrada."""
    saida = RE_CNPJ.sub("[CNPJ]", texto)
    saida = RE_CPF.sub("[CPF]", saida)
    saida = RE_EMAIL.sub("[E-MAIL]", saida)
    saida = RE_FONE.sub("[TELEFONE]", saida)
    for nome in sorted((n for n in nomes if n and n.strip()), key=len, reverse=True):
        saida = re.sub(re.escape(nome.strip()), "[CLIENTE]", saida, flags=re.IGNORECASE)
    return saida


def validar_respostas(r):
    """Devolve lista de problemas (vazia = ok)."""
    erros = [f"campo obrigatório ausente: {c}" for c in CAMPOS_OBRIGATORIOS if not r.get(c)]
    for i, t in enumerate(r.get("testes") or [], 1):
        if not t.get("entrada") or not t.get("deve_conter"):
            erros.append(f"teste {i} precisa de 'entrada' e 'deve_conter'")
    if len(r.get("testes") or []) < 3:
        erros.append("são necessários 3 testes")
    return erros


def _lista(itens, numerada=False):
    if numerada:
        return "\n".join(f"{i}. {x}" for i, x in enumerate(itens, 1))
    return "\n".join(f"- {x}" for x in itens)


def montar_instrucoes(r):
    nunca = list(NUNCA_PADRAO) + list(r.get("nunca") or [])
    erros = r.get("erros_comuns") or []
    tom = r.get("tom") or ("Conversa de colega de profissão: direto, prático, sem enrolação, sem jargão "
                           "corporativo, sem frase motivacional. Português do Brasil.")
    partes = [
        f"# Instruções fixas: {r['titulo']}",
        "## Quem você é e para quê\n"
        f"Você é a assistente de [NOME DA CONSULTORA], consultoria de alimentos. {r['objetivo']}\n"
        f"Quem recebe o resultado: {r['destinatario']}.",
        "## O que vou te enviar\n" + _lista(r["entradas"]) +
        "\n\nSe a minha primeira mensagem não trouxer isso, NÃO produza a entrega. "
        "Mostre esta lista e peça o que falta, uma vez só, de forma curta.",
        "## Passo a passo (nesta ordem)\n" + _lista(r["passos"], numerada=True),
        "## Formato da resposta\n"
        "Siga o arquivo `modelo-da-entrega.md`: mesmos títulos, mesma ordem. "
        "Use o `exemplo-bom.md` como régua de qualidade e de tamanho, nunca copie o conteúdo dele. "
        "Consulte o `base-da-area.md` para saber o que conferir.",
        "## Nunca faça\n" + _lista(nunca),
        "## Regra do \"conferir\"\n"
        "Tudo que depende de norma, legislação, limite ou prazo vai marcado `[conferir vigência]`. "
        "Você pode citar só o NOME da norma-base como indicação de onde olhar, sempre com "
        "\"(conferir vigente)\". Nunca cite artigo, item ou número que eu não tenha enviado. "
        "No fim da entrega, liste num bloco \"Conferir antes de enviar\" tudo que marcou.",
        f"## Tom\n{tom}",
    ]
    if erros:
        partes.append("## Erros que eu mais corrijo (evite)\n" + _lista(erros))
    partes.append(
        "## Antes de entregar, confira\n"
        "- Todos os títulos do modelo estão na ordem?\n"
        "- Algum número, norma ou prazo foi marcado `[conferir]`?\n"
        "- Tem nome de pessoa, CNPJ ou CPF? Troque por [CLIENTE].\n"
        "- Fecha com o próximo passo concreto e o bloco \"Conferir antes de enviar\"?\n"
        "- É um rascunho para eu revisar: diga isso em uma linha no fim."
    )
    return "\n\n".join(partes) + "\n"


def montar_modelo(r):
    linhas = [f"# Modelo da entrega: {r['titulo']}", "",
              "Copie esta estrutura. Troque o que está entre [colchetes]. Não apague títulos.", ""]
    for s in r["modelo_secoes"]:
        linhas += [f"## {s['titulo']}", f"[{s['instrucao']}]", ""]
    linhas += ["## Conferir antes de enviar",
               "[Lista de tudo que foi marcado como conferir: norma, número, prazo, valor.]", ""]
    return "\n".join(linhas)


def montar_base(r):
    linhas = [f"# Base da área: {r['titulo']}", "",
              "Anexe ao projeto os documentos abaixo (versão que VOCÊ baixou da fonte oficial). "
              "A IA não deve citar nada além do que estiver aqui ou do que você enviar.", "",
              "| Referência | Para que serve | Onde pegar | Status |",
              "|---|---|---|---|"]
    for ref in r["referencias"]:
        linhas.append(f"| {ref['nome']} | {ref['para_que']} | {ref.get('onde', 'fonte oficial do órgão')} "
                      "| conferir vigência |")
    linhas += ["", "## Como manter",
               "- Antes de usar, abra a fonte oficial e confirme que a versão anexada está vigente.",
               "- Anote aqui a data da última conferência: ____/____/______",
               "- Norma estadual ou municipal muda de lugar para lugar: use a do local do cliente.",
               "- Sem a fonte anexada, a IA marca `[conferir]` em vez de responder.", ""]
    return "\n".join(linhas)


def montar_exemplo(r):
    texto = anonimizar(r["exemplo_bom"], r.get("anonimizar") or [])
    return ("# Exemplo bom (anonimizado)\n\n"
            "Este é o nível de qualidade esperado. Dados trocados por [CLIENTE] e [EMPRESA].\n\n"
            "---\n\n" + texto.strip() + "\n")


def montar_teste(r):
    linhas = [f"# Teste do projeto: {r['titulo']}", "",
              "Rode cada entrada abaixo no projeto novo. Se a saída não tiver tudo da lista, "
              "ajuste `instrucoes.md` (uma mudança por vez) e rode de novo.", ""]
    for i, t in enumerate(r["testes"], 1):
        linhas += [f"## Teste {i}", "**Cole no projeto:**", "```", t["entrada"].strip(), "```",
                   "**A resposta boa precisa ter:**", _lista(t["deve_conter"]), ""]
    linhas += ["## Teste fixo (sempre)",
               "**Cole:** \"Qual é o artigo e o limite exato da norma sobre isso?\"",
               "**A resposta boa precisa ter:**",
               "- Recusa em inventar número",
               "- Marca `[conferir]` e indica onde olhar (fonte oficial)", ""]
    return "\n".join(linhas)


COMO_USAR = """# Como usar este pacote (1 página)

Você tem 6 arquivos. Três vão para o projeto: `modelo-da-entrega.md`, `base-da-area.md`, `exemplo-bom.md`.
O texto de `instrucoes.md` vai no campo de instruções. `teste.md` é só para você testar.

> Os nomes de botões podem mudar: as plataformas atualizam o visual toda hora. Procure o equivalente.

## Claude (Projects)
1. Entre em claude.ai e abra **Projects** no menu lateral.
2. Clique em **Create project** (ou **New project**). Dê o nome da tarefa.
3. Procure **Set project instructions** (ou **Instructions**). Cole todo o `instrucoes.md`.
4. Em **Add content / Files**, anexe `modelo-da-entrega.md`, `base-da-area.md`, `exemplo-bom.md` e os documentos oficiais da base.
5. Abra uma conversa dentro do projeto e rode o `teste.md`.

## Gemini (Gems)
1. Entre em gemini.google.com e abra **Gem manager** (ou **Explore Gems**).
2. Clique em **New Gem**. Dê o nome da tarefa.
3. No campo de instruções, cole o `instrucoes.md`. Se não couber, cole as seções "Quem você é", "Passo a passo", "Nunca faça" e "Regra do conferir" e deixe o resto nos arquivos.
4. Em **Knowledge / Add files**, anexe os 3 arquivos de apoio e os documentos oficiais.
5. Salve e teste com o `teste.md`.

## ChatGPT (GPTs personalizados)
1. Entre em chatgpt.com, abra **Explore GPTs** e clique em **Create** (precisa de plano que permita criar GPTs).
2. Vá na aba **Configure**. Preencha **Name** e **Description**.
3. Em **Instructions**, cole o `instrucoes.md` (limite de cerca de 8.000 caracteres: o arquivo já respeita).
4. Em **Knowledge**, faça upload dos 3 arquivos de apoio e dos documentos oficiais.
5. Deixe **Web search** desligado se quiser que ele só use a sua base. Salve em **Only me**.

## Depois de montar
- Rode os 3 testes do `teste.md` e o teste fixo.
- Use de verdade 3 vezes. Cada erro que você corrigir à mão vira uma linha em "Nunca faça" ou "Erros que eu mais corrijo".
- Revise toda saída antes de mandar ao cliente: é rascunho. Tudo marcado `[conferir]` você confere na fonte oficial.
- Não suba CNPJ, CPF ou dados pessoais de cliente. Use [CLIENTE].
"""


def gerar(respostas, saida):
    """Valida e escreve os 6 arquivos. Devolve a lista de caminhos. Levanta ValueError se inválido."""
    erros = validar_respostas(respostas)
    if erros:
        raise ValueError("; ".join(erros))
    instrucoes = montar_instrucoes(respostas)
    if len(instrucoes) > LIMITE_INSTRUCOES:
        raise ValueError(f"instrucoes.md tem {len(instrucoes)} caracteres (limite {LIMITE_INSTRUCOES}). "
                         "Enxugue passos, 'nunca' ou erros_comuns.")
    destino = Path(saida)
    destino.mkdir(parents=True, exist_ok=True)
    conteudos = {
        "instrucoes.md": instrucoes,
        "modelo-da-entrega.md": montar_modelo(respostas),
        "base-da-area.md": montar_base(respostas),
        "exemplo-bom.md": montar_exemplo(respostas),
        "teste.md": montar_teste(respostas),
        "COMO-USAR.md": COMO_USAR,
    }
    caminhos = []
    for nome, texto in conteudos.items():
        p = destino / nome
        p.write_text(texto, encoding="utf-8", newline="\n")
        caminhos.append(p)
    return caminhos


def validar_pacote(pasta):
    """Confere um pacote já gerado. Devolve lista de problemas."""
    pasta = Path(pasta)
    problemas = [f"falta {a}" for a in ARQUIVOS if not (pasta / a).exists()]
    if problemas:
        return problemas
    instr = (pasta / "instrucoes.md").read_text(encoding="utf-8")
    if len(instr) > LIMITE_INSTRUCOES:
        problemas.append(f"instrucoes.md com {len(instr)} caracteres")
    if "conferir" not in instr.lower():
        problemas.append("instrucoes.md sem a regra do conferir")
    if "inventar número" not in instr.lower():
        problemas.append("instrucoes.md sem a proibição de inventar norma/número")
    for a in ARQUIVOS:
        if a == "teste.md":
            continue  # entradas de teste trazem dados falsos de propósito
        t = (pasta / a).read_text(encoding="utf-8")
        for rx, nome in ((RE_CNPJ, "CNPJ"), (RE_CPF, "CPF"), (RE_EMAIL, "e-mail"), (RE_FONE, "telefone")):
            if rx.search(t):
                problemas.append(f"{a} contém {nome}")
    return problemas


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("respostas", nargs="?", help="JSON com as respostas da entrevista")
    ap.add_argument("--saida", help="pasta de saída (padrão: ao lado do JSON)")
    ap.add_argument("--validar", metavar="PASTA", help="só valida um pacote já gerado")
    args = ap.parse_args(argv)
    if args.validar:
        probs = validar_pacote(args.validar)
        print("OK" if not probs else "\n".join(probs))
        return 1 if probs else 0
    if not args.respostas:
        ap.error("informe o JSON de respostas ou --validar PASTA")
    jpath = Path(args.respostas)
    saida = args.saida or jpath.parent
    try:
        respostas = json.loads(jpath.read_text(encoding="utf-8-sig"))
        caminhos = gerar(respostas, saida)
    except json.JSONDecodeError as e:
        print(f"Erro: o arquivo JSON está inválido (linha {e.lineno}, coluna {e.colno}): {e.msg}")
        return 1
    except UnicodeDecodeError:
        print("Erro: não consegui ler o arquivo. Salve o JSON como UTF-8.")
        return 1
    except PermissionError:
        print("Erro: não consegui salvar. Feche o arquivo no Word e rode de novo.")
        return 1
    except (ValueError, OSError) as e:
        print(f"Erro: {e}")
        return 1
    for c in caminhos:
        print(f"escrito: {c}")
    probs = validar_pacote(saida)
    if probs:
        print("Atenção: " + "; ".join(probs))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
