"""Estabelecimentos do MAPA em DADOS ABERTOS (portal CKAN oficial, sem login).

Uso:
  python -I mapa_dados.py sif     [--razao t] [--fantasia t] [--cnpj 14dig] [--nr-sif N] [--uf SP] [--municipio t] [--area t] [--situacao A] [--n 20]
  python -I mapa_dados.py bebidas [--razao t] [--registro SP0013196] [--uf SP] [--municipio t] [--atividade t] [--classificacao t] [--status Ativo] [--n 20]
  (ambos aceitam --csv ARQUIVO para teste offline)

sif     = Estabelecimentos Registrados no SIF (dataset servico-de-inspecao-federal-sif)
bebidas = SIPEAGRO, Vinhos e Bebidas (dataset sipeagro): registro de estabelecimento (CNPJ vem mascarado)
A URL do CSV e descoberta pela API CKAN (package_show), entao nao quebra quando o arquivo muda de endereco.
Mostra a data da ultima modificacao do arquivo. Nao imprime e-mail nem telefone da empresa.
So estabelecimentos: registro de PRODUTO de bebida nao esta nestes dados.
Fora do escopo (sem dado aberto): SISBI/e-Sisbi, SIE e SIM estaduais/municipais; SISLEGIS exige login.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # necessario com python -I
import _dados_abertos as da  # noqa: E402

CKAN = "https://dados.agricultura.gov.br/api/3/action/package_show?id="
FONTES = {
    "sif": {"pacote": "servico-de-inspecao-federal-sif", "recurso": "Estabelecimentos Registrados no SIF"},
    "bebidas": {"pacote": "sipeagro", "recurso": "Vinhos e Bebidas"},
}


def localizar_recurso(chave: str):
    f = FONTES[chave]
    pacote = da.json_de(CKAN + f["pacote"], f"ckan_{f['pacote']}.json")["result"]
    alvo = da.norm(f["recurso"])
    for r in pacote["resources"]:
        if da.norm(r.get("name", "")) == alvo and (r.get("format") or "").upper() == "CSV":
            return r["url"], r.get("last_modified") or pacote.get("metadata_modified")
    raise da.SemAcesso(f"recurso '{f['recurso']}' nao encontrado no pacote {f['pacote']} (layout do portal mudou?)")


def filtrar_sif(linhas, razao=None, fantasia=None, cnpj=None, nr_sif=None, uf=None, municipio=None, area=None,
                situacao=None):
    cnpj = da.so_digitos(cnpj) if cnpj else None
    for r in linhas:
        if razao and not da.contem(r.get("RAZAO_SOCIAL", ""), razao):
            continue
        if fantasia and not da.contem(r.get("NOME_FANTASIA", ""), fantasia):
            continue
        if cnpj and da.so_digitos(r.get("CPF_CNPJ", "")) != cnpj:
            continue
        if nr_sif and da.so_digitos(r.get("NR_SIF", "")) != da.so_digitos(nr_sif):
            continue
        if uf and r.get("UF", "").upper() != uf.upper():
            continue
        if municipio and not da.contem(r.get("MUNICIPIO", ""), municipio):
            continue
        if area and not da.contem(r.get("AREA_CATEGORIA", ""), area):
            continue
        if situacao and r.get("SITUACAO", "").upper() != situacao.upper():
            continue
        yield r


def filtrar_bebidas(linhas, razao=None, registro=None, uf=None, municipio=None, atividade=None,
                    classificacao=None, status=None):
    for r in linhas:
        if razao and not da.contem(r.get("RAZAO_SOCIAL", ""), razao):
            continue
        if registro and da.norm(r.get("NUMERO_REGISTRO_ESTABELECIMENTO", "")) != da.norm(registro):
            continue
        if uf and r.get("UF", "").upper() != uf.upper():
            continue
        if municipio and not da.contem(r.get("MUNICIPIO", ""), municipio):
            continue
        if atividade and not da.contem(r.get("ATIVIDADE", ""), atividade):
            continue
        if classificacao and not da.contem(r.get("CLASSIFICACAO", ""), classificacao):
            continue
        if status and da.norm(r.get("STATUS_DO_REGISTRO", "")) != da.norm(status):
            continue
        yield r


ROTULOS = {
    "sif": [("Razao social", "RAZAO_SOCIAL"), ("Fantasia", "NOME_FANTASIA"), ("CNPJ", "CPF_CNPJ"),
            ("SIF n", "NR_SIF"), ("Situacao (A=ativo)", "SITUACAO"), ("Municipio/UF", None),
            ("Area", "AREA_CATEGORIA"), ("Categoria/classe", "CATEGORIA_CLASSE"),
            ("Registro em", "DT_REGISTRO"), ("Ocorrencia", "DESCRICAO_OCORRENCIA")],
    "bebidas": [("Razao social", "RAZAO_SOCIAL"), ("Registro estabelecimento", "NUMERO_REGISTRO_ESTABELECIMENTO"),
                ("Status", "STATUS_DO_REGISTRO"), ("CNPJ (mascarado)", "CPF_CNPJ"), ("Municipio/UF", None),
                ("Area", "AREA_ATUACAO"), ("Atividade", "ATIVIDADE"), ("Classificacao", "CLASSIFICACAO")],
}


def formatar(chave: str, r) -> str:
    out = []
    for rot, k in ROTULOS[chave]:
        v = f"{r.get('MUNICIPIO', '')}/{r.get('UF', '')}" if k is None else r.get(k, "")
        if v and v != "/":
            out.append(f"  {rot}: {v}")
    return "\n".join(out)


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sif")
    for o in ("razao", "fantasia", "cnpj", "nr-sif", "uf", "municipio", "area", "situacao"):
        s.add_argument("--" + o)
    b = sub.add_parser("bebidas")
    for o in ("razao", "registro", "uf", "municipio", "atividade", "classificacao", "status"):
        b.add_argument("--" + o)
    for p in (s, b):
        p.add_argument("--n", type=int, default=20)
        p.add_argument("--csv")
    a = ap.parse_args(argv)
    filtros = {k: v for k, v in vars(a).items() if k not in ("cmd", "n", "csv") and v}
    if not filtros:
        ap.error("informe ao menos um filtro")
    try:
        if a.csv:
            with open(a.csv, "rb") as f:
                dados = f.read()
            url, mod = a.csv, "arquivo local"
        else:
            url, mod = localizar_recurso(a.cmd)
            dados = da.baixar(url, f"mapa_{a.cmd}.csv")
    except da.SemAcesso as e:
        da.sair_erro(f"{e}. Caminho manual: https://dados.agricultura.gov.br/ (busque o conjunto).")
    linhas = list(da.linhas_csv(dados))
    fn = filtrar_sif if a.cmd == "sif" else filtrar_bebidas
    achados = list(fn(linhas, **filtros))
    print(f"FONTE: {url}")
    print(f"ARQUIVO MODIFICADO EM: {mod} | linhas: {len(linhas)} | encontradas: {len(achados)}")
    for r in achados[: a.n]:
        print("-" * 60)
        print(formatar(a.cmd, r))
    if len(achados) > a.n:
        print(f"... mais {len(achados) - a.n} (use --n ou filtre mais)")
    if not achados:
        print("Nada encontrado neste arquivo.")
    print("CONFERIR: dado aberto ate a data acima; confirme com o MAPA/SFA antes de usar com cliente.")


if __name__ == "__main__":
    main()
