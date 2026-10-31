---
name: documento-tecnico-fran
description: Gera documento técnico de Boas Práticas em .docx adaptado ao cliente da consultora, a partir do modelo DELA (se tiver) ou dos esqueletos do método Fran. Cobre POP, Manual de Boas Práticas (MBP/MBPF), ficha técnica de preparo/produto, PAC (programa de autocontrole) e planilhas de controle (temperatura, higienização, recebimento). Use quando a consultora pedir "fazer POP", "manual de boas práticas", "MBP", "MBPF", "ficha técnica", "PAC", "programa de autocontrole", "planilha de controle", "ficha de registro", "adaptar meu modelo", "usar meu modelo", ou soltar um .docx/.pdf de modelo dela. NÃO é relatório de visita (visita-fran), nem consulta de norma (regulatorio-fran), nem preço do serviço (val-fran).
---

# Documento técnico (POP, MBP, ficha técnica, PAC, planilhas)

Quem executa: agente `bpf-fran` (Bia). Regras que vencem esta skill: `core/constituicao.md` e `core/voz-fran.md`. Decisão do squad: **a IA faz o rascunho, a consultora confere.** O arquivo sai com as pendências marcadas, nunca como "pronto para fiscalização" (constituição §4).

Pasta da skill: `<SQUAD>/skills/documento-tecnico-fran/`
- `gerar_documento.py` gera o .docx a partir de um JSON.
- `modelos/` esqueletos por tipo: `pop.md`, `mbp.md`, `ficha-tecnica.md`, `pac.md`, `planilhas.md`.
- `exemplos/pop-exemplo.json` e `pop-exemplo.docx` (padaria fictícia).

## Passo a passo

1. **Identifique o tipo** do documento: `pop`, `mbp`, `ficha_tecnica`, `pac` ou `planilha`. Pedido ambíguo: pergunte. "PAC" aqui é programa de autocontrole (produto de origem animal, MAPA); na base da Fran PAC também é o Programa de Aceleração em Consultoria, outro assunto.
2. **Briefing: no máximo 5 perguntas, uma por vez**, só as que mudam o documento:
   1. Tipo de estabelecimento (padaria, restaurante, indústria, produto de origem animal...)?
   2. Porte?
   3. Nº de funcionários (e turnos)?
   4. Processos ou produtos principais?
   5. O que já existe (manuais, POPs, planilhas) e se ela tem **modelo próprio**?
   Pergunte primeiro a referência prática do método (veja o esqueleto do tipo) e só depois os dados.
3. **Modelo da consultora tem prioridade.** Se ela mandou .docx ou .pdf:
   - Leia a estrutura (títulos, ordem, tabelas, colunas): `python -I -c "import docx,sys; d=docx.Document(sys.argv[1]); [print(p.style.name,'|',p.text) for p in d.paragraphs if p.text.strip()]" modelo.docx` (PDF: extraia o texto).
   - **Mantenha as seções, a ordem e os títulos DELA** e preencha com os dados do cliente. Não "melhore" a estrutura; se achar lacuna, aponte em `flags`, não reescreva.
   - Sem modelo: use o esqueleto em `modelos/<tipo>.md` (vem dos modelos do curso da Fran).
4. **Referências a requisitos (norma, artigo, limite): só via `regulatorio-fran` com consulta ao vivo.** Sem consulta, escreva só o nome da norma-base com "(conferir vigente)" ou deixe "⚠️ referência a conferir". Nunca de memória (constituição §3).
5. **Números (temperatura, tempo, concentração, %, validade) levam "⚠️ conferir"** a menos que tenham vindo de consulta ao vivo. Só então preencha `fonte_conferida` na seção (ex.: "RDC xxx art. y, lida em dd/mm/aaaa, link"), o que tira a flag daquela seção. O gerador também marca sozinho; não dependa disso, escreva já com a flag onde souber.
6. **Frequência e rotina são prática do método ou do cliente, não exigência legal.** Escreva assim e registre em `flags` para validar com o dono.
7. **Monte o JSON e gere o .docx** (formato abaixo). Salve em `clients/<cliente>/docs/` do workspace da consultora ou onde ela indicar.
8. **Passe pela `revisora-fran`** (checklist: norma citada, promessa sanitária, voz, próximo passo, dado pessoal) antes de entregar. Corrija os bloqueios e gere de novo.
9. **Entregue** com 3 linhas: onde está o arquivo; quantas pendências ⚠️ ficaram (ela confere cada uma e apaga a página de pendências); **Próximo passo:** uma ação para hoje (ex.: validar o POP com o dono e com quem executa). Cite `(Fonte: curso › módulo › aula)` quando usar a base.

## Regras por tipo

- **POP:** um POP = uma tarefa, sempre com ficha de registro (tabela com linhas em branco) amarrada ao número. Ouvir dono e quem manipula. Não crie todos os POPs de uma vez: priorize o primeiro mês.
- **MBP/MBPF:** serviço de alimentação = manual + POPs + planilhas juntos; indústria = manual e procedimentos em documentos separados. Logo e foto do CLIENTE na capa. Descreva a empresa como ela deve ser.
- **Planilha de controle:** `tipo: "planilha"` (paisagem). Defina quem preenche, quando e com que frequência. Faixa de temperatura aceita = ⚠️ conferir.
- **PAC:** sem modelo no curso; esqueleto geral. Lista de elementos e critérios só com consulta ao vivo.
- **Ficha técnica:** mostre os cálculos com a fórmula escrita (rendimento, per capita, custo por porção, CMV). Use `calcular_ficha(custo_total, rendimento_porcoes, preco_venda)` do script, que devolve o número e a fórmula em texto, e cole a fórmula numa seção "Cálculos". Insumo com preço e FC vêm do cliente; FC teórico é ponto de partida (⚠️ conferir). **Tabela nutricional NÃO é calculada: só estrutura com células em branco** e a nota de nutricionista/CRN (o gerador recusa valor preenchido). Não prometa informação nutricional pronta.

## Formato do JSON

```json
{
  "tipo": "pop | mbp | ficha_tecnica | pac | planilha",
  "cliente": "Nome do cliente",
  "titulo": "POP 01 - Higienização das instalações",
  "codigo": "POP-01", "versao": "1.0", "data": "dd/mm/aaaa",
  "elaborado_por": "...", "aprovado_por": "...",
  "flags": ["Pendência livre a validar com o cliente"],
  "secoes": [
    {"titulo": "Objetivo", "conteudo": "texto ou lista de parágrafos"},
    {"titulo": "Procedimento", "itens": ["passo 1", "passo 2"]},
    {"titulo": "Ficha de registro",
     "tabela": {"colunas": ["Data", "Local"], "linhas": [["", ""]], "linhas_vazias": 8}},
    {"titulo": "Base", "conteudo": "...", "fonte_conferida": "norma, artigo, data, link"}
  ]
}
```

Gerar: `python "{{SQUAD_ROOT}}/skills/documento-tecnico-fran/gerar_documento.py" entrada.json -o saida.docx`

O .docx sai com: cabeçalho (cliente, documento, código, versão, data, elaborado/aprovado por), seções numeradas, tabelas, bloco de assinaturas, página de pendências (desligue com `"incluir_pendencias": false` só depois de conferir tudo) e rodapé "cliente · documento · versão · data" com número de página. Texto com marca de ferramenta/IA é recusado; o arquivo não leva essa marca em lugar nenhum.

## Limites (avise a consultora)
- O documento é rascunho técnico: a responsabilidade técnica é dela. Não garante aprovação em fiscalização.
- Dado de cliente: não coloque CPF, CNPJ completo nem dado pessoal além do necessário (constituição §7).
- O gerador não lê PDF nem converte o modelo dela sozinho: você lê a estrutura (passo 3) e monta o JSON.
- Testes: `python -m pytest tests/test_documento_tecnico.py -q` (na raiz do squad).
