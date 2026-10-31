"""Consulta de alimento/aditivo/embalagem regularizado na Anvisa, via DADOS ABERTOS (CSV oficial).

Uso:
  python -I anvisa_alimentos.py [--produto "texto"] [--empresa "texto"] [--cnpj 14digitos]
         [--registro NUM] [--categoria "texto"] [--situacao Ativo|Inativo] [--n 20] [--csv ARQUIVO]
Fonte: https://dados.anvisa.gov.br/dados/CONSULTAS/PRODUTOS/TA_CONSULTA_ALIMENTOS.CSV
Mostra a data da carga do CSV (DT_CARGA_ETL): a consulta vale ate essa data, nunca e "tempo real".
Lembrete: a maioria dos alimentos e dispensada de registro; confira a norma vigente na fonte com
anvisalegis.py. Ausencia neste CSV NAO prova irregularidade.
O site consultas.anvisa.gov.br responde 403 a ferramentas; este CSV e o caminho aberto.
"""
import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # necessario com python -I
import _dados_abertos as da  # noqa: E402

URL = "https://dados.anvisa.gov.br/dados/CONSULTAS/PRODUTOS/TA_CONSULTA_ALIMENTOS.CSV"


def filtrar(linhas, produto=None, empresa=None, cnpj=None, registro=None, categoria=None, situacao=None):
    cnpj = da.so_digitos(cnpj) if cnpj else None
    registro = da.so_digitos(registro) if registro else None
    for r in linhas:
        if produto and not (da.contem(r.get("NO_PRODUTO", ""), produto) or da.contem(r.get("MARCAS", ""), produto)):
            continue
        if empresa and not da.contem(r.get("NO_RAZAO_SOCIAL_EMPRESA", ""), empresa):
            continue
        if cnpj and da.so_digitos(r.get("NU_CNPJ_EMPRESA", "")) != cnpj:
            continue
        if registro and registro not in (da.so_digitos(r.get("NU_REGISTRO_NOTIFICACAO_PRODUTO", "")),
                                         da.so_digitos(r.get("NU_REGISTRO_PRODUTO", ""))):
            continue
        if categoria and not da.contem(r.get("DS_CATEGORIA_PRODUTO", ""), categoria):
            continue
        if situacao and da.norm(r.get("SITUACAO_REGISTRO", "")) != da.norm(situacao):
            continue
        yield r


def formatar(r) -> str:
    campos = [
        ("Produto", "NO_PRODUTO"), ("Marca", "MARCAS"), ("Categoria", "DS_CATEGORIA_PRODUTO"),
        ("Tipo", "TIPO_REGULARIZACAO"), ("Registro/notificacao", "NU_REGISTRO_NOTIFICACAO_PRODUTO"),
        ("Situacao do registro", "SITUACAO_REGISTRO"), ("Situacao do assunto", "DS_SITUACAO_ASSUNTO_DOC"),
        ("Vencimento (MMAAAA)", "DT_VENCIMENTO_REGISTRO"), ("Empresa", "NO_RAZAO_SOCIAL_EMPRESA"),
        ("CNPJ", "NU_CNPJ_EMPRESA"), ("Alegacao funcional", "DS_ALEGACAO_FUNCIONAL"),
    ]
    return "\n".join(f"  {rot}: {r.get(k, '')}" for rot, k in campos if r.get(k, ""))


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for o in ("produto", "empresa", "cnpj", "registro", "categoria", "situacao"):
        ap.add_argument("--" + o)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--csv", help="usar arquivo local (teste/offline) em vez de baixar")
    a = ap.parse_args(argv)
    if not any([a.produto, a.empresa, a.cnpj, a.registro, a.categoria]):
        ap.error("informe ao menos --produto, --empresa, --cnpj, --registro ou --categoria")
    try:
        if a.csv:
            with open(a.csv, "rb") as f:
                dados = f.read()
        else:
            dados = da.baixar(URL, "anvisa_alimentos.csv")
    except da.SemAcesso as e:
        da.sair_erro(f"{e}. Caminho manual: https://consultas.anvisa.gov.br/#/alimentos/ (navegador).")
    linhas = list(da.linhas_csv(dados))
    cargas = Counter(r.get("DT_CARGA_ETL", "")[:10] for r in linhas)
    carga = cargas.most_common(1)[0][0] if cargas else "?"
    achados = list(filtrar(linhas, a.produto, a.empresa, a.cnpj, a.registro, a.categoria, a.situacao))
    print(f"FONTE: {URL}")
    print(f"CARGA DO CSV: {carga} | linhas no arquivo: {len(linhas)} | encontradas: {len(achados)}")
    for r in achados[: a.n]:
        print("-" * 60)
        print(formatar(r))
    if len(achados) > a.n:
        print(f"... mais {len(achados) - a.n} (use --n ou filtre mais)")
    if not achados:
        print("Nada encontrado neste CSV (nao prova que o produto seja irregular: veja dispensa de registro).")
    print("CONFERIR: dado aberto ate a data de carga; confirme no site da Anvisa antes de usar com cliente.")


if __name__ == "__main__":
    main()
