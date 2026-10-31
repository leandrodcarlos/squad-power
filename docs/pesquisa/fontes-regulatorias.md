# Fontes regulatórias oficiais: como o agente `regulatorio-fran` consulta ao vivo

Pesquisa feita e testada em 29/10/2026 (curl no Windows, WebFetch, WebSearch). Tudo abaixo foi executado de verdade; o que não foi testado está marcado.
Regra do agente: nunca responder norma de memória. Cada resposta traz: nome/número da norma, link oficial, trecho citado, data da consulta e flag "conferir".

## 1. Resumo

- Funcionam bem sem login: AnvisaLegis (RDC com status de vigência), DOU/in.gov.br (busca e texto de publicação), BVS/Saúde Legis (texto HTML), Planalto (só via WebFetch), WebSearch como localizador.
- Bloqueadas ou frágeis: SISLEGIS/MAPA (redireciona para login), CVS-SP (PDFs 403 no curl), Codex (timeout), Planalto via curl (falha TLS), site de consulta de produto da Anvisa (403; usar os dados abertos, receita 3.7), Inmetro registro (sem script), Vigilâncias de PR e MG (sem acervo pesquisável testado).
- Armadilha de desambiguação: "IN 75" existe na Anvisa (IN 75/2020, rotulagem nutricional) e no MAPA (IN 75/2019, bebidas, vinhos e derivados). O agente SEMPRE pergunta ou declara o órgão antes de buscar.
- O portal antigo `gov.br/anvisa/.../alimentos/legislacao` hoje redireciona (302) para o AnvisaLegis. A Anvisa migrou a legislação para lá.

## 2. Tabela por fonte

Confiabilidade: 1 (não usar sozinho) a 5 (usar como fonte principal).

| Fonte | URL base | Método que funcionou | Formato | Mostra vigência/revogação? | Bloqueios | Conf. |
|---|---|---|---|---|---|---|
| ANVISA, AnvisaLegis | `https://anvisalegis.datalegis.net` | URL de ato por parâmetros (ver receita 3.1). Testado: RDC 429/2020 OK, RDC 275/2002 OK, RDC 216/2004 OK | HTML (latin1/iso-8859-1) com texto integral e notas de alteração | SIM. Rótulo "Vigente", "Vigente com Alterações" no cabeçalho; artigos aparecem "(Revogado pela RDC nº X)" | Home e busca livre são carregadas por JS (curl só vê o casco). IN usa `tipo=INM` (ver 3.1); algumas RDC exigem `seqAto=002` | 4 para RDC e IN (`tipo=INM`) |
| ANVISA, Biblioteca temática de Alimentos (compilado de normas vigentes) | `gov.br/anvisa/pt-br/assuntos/regulamentacao/legislacao/bibliotecas-tematicas/arquivos/biblioteca-de-alimentos` e `anvisalegis...acao=recuperarTematicasCollapse&cod_modulo=135&cod_menu=1686` | Link do próprio site da Anvisa (achado no menu do AnvisaLegis) | Era PDF; hoje a URL do PDF devolve 404 e a versão temática fica dentro do AnvisaLegis (JS) | A Anvisa diz que atualiza "periodicamente"; data não verificável por curl | URL do PDF 404; página temática é JS-only | 2 (usar só como índice, nunca como texto citado) |
| ANVISA, consulta de produtos/registro (site) | `consultas.anvisa.gov.br` | API do site: 403 para ferramenta (testado 30/10/2026). NÃO contornar. Use os dados abertos (linha seguinte) | SPA | n/a | 403 | 1 (só manual, no navegador) |
| ANVISA, dados abertos (CSV de alimentos regularizados) | `dados.anvisa.gov.br/dados/CONSULTAS/PRODUTOS/TA_CONSULTA_ALIMENTOS.CSV` | HTTP direto, sem login (30/10/2026: 200, 34 MB, 67 mil linhas, carga de 12/10/2026). Script `anvisa_alimentos.py` | CSV ';' UTF-8 | Traz situação do registro e vencimento, não a norma | Atualização periódica (veja DT_CARGA_ETL); só o que tem registro/notificação. Alimento dispensado de registro não aparece | 4 (para 'este produto tem registro?', com a data da carga) |
| MAPA, SISLEGIS | `sistemasweb.agricultura.gov.br/sislegis` | Todas as rotas testadas (consultar, detalhaAto, visualizarAtoPortalMapa) | HTML | Sim, quando acessível | 302 para `loginAction.do` (exige sessão) ou 500 | 1 (não depender) |
| MAPA, wiki DIPOA (base legal em PDF) | `wikisda.agricultura.gov.br/dipoa_baselegal/<arquivo>.pdf` | `curl` direto. Testado: `port_368-1997_bpf.pdf` (Portaria 368/1997, 11 pág., texto extraível) | PDF com texto | NÃO. É impressão do SISLEGIS de 05/07/2023, sem status | Diretório sem listagem (404); nome do arquivo precisa vir do WebSearch | 3 para texto original; vigência exige outra fonte |
| MAPA, gov.br/agricultura (listas de legislação) | `gov.br/agricultura/pt-br/assuntos/inspecao/produtos-animal/legislacao` | WebFetch/curl (HTML, 340 KB). Mostra "atualizado em 28/09/2026" e links para Planalto e PDFs | HTML com links | Parcial (a página é atualizada, o ato linkado não diz status) | Algumas URLs de anexos (Cartilhão de Bebidas, IN 140/2024) devolvem 404 no curl; achar a URL atual via WebSearch | 3 |
| MAPA, Cartilhão de Bebidas (IN 140/2024, 6ª ed., atualizada até 06/09/2025) | gov.br/agricultura, "biblioteca de normas de vinhos e bebidas" | Só localizado por WebSearch; URL direta 404 | PDF | Consolidado (diz "atualizado até") | URL muda | 3 (conferir data de corte) |
| MAPA, dados abertos (SIF e SIPEAGRO bebidas) | `dados.agricultura.gov.br` (CKAN) | API `package_show` sem login lista os CSV; script `mapa_dados.py` (30/10/2026: SIF 36.639 estabelecimentos, arquivo de 02/10/2026; bebidas 31.945 linhas, arquivo de 25/10/2026) | CSV ';' UTF-8 (alguns acentos já vêm corrompidos na origem) | Só situação do registro do estabelecimento | Só estabelecimento (não há registro de produto de bebida); CNPJ de bebidas vem mascarado; SISBI/SIE/SIM não têm dado aberto | 4 (com a data do arquivo) |
| Diário Oficial da União | `www.in.gov.br` | Busca: `https://www.in.gov.br/consulta/-/buscar/dou?q=<frase entre aspas>&s=do1&exactDate=all&sortType=1&delta=5`. Texto: `https://www.in.gov.br/web/dou/-/<urlTitle>` (o `urlTitle` vem na busca) | Busca: HTML com JSON embutido (`"jsonArray":[...]`); ato: HTML | NÃO diz vigência (é o texto publicado). Serve para achar norma nova e confirmar publicação original | Query sem aspas devolve resultado irrelevante e ordenado por data. Frase exata do título ou da ementa funciona. URL de ato com slug inventado dá 404 | 4 |
| Saúde Legis / BVS (Ministério da Saúde, acervo de portarias e RDC antigas) | `bvsms.saude.gov.br/bvs/saudelegis/...` | URL estática por padrão `.../anvisa/2002/rdc0275_21_10_2002.html` (OK, 47 KB). `.../gm/2017/prc0005_03_10_2017.html` OK (12 MB, 13 s) | HTML/PDF (nem todo ato existe; RDC 429 em PDF deu 404) | NÃO. Traz aviso "texto não substitui o publicado no DOU" e não marca alterações | Nome do arquivo exige conhecer o padrão; arquivos enormes | 3 |
| Planalto (leis e decretos) | `www.planalto.gov.br/ccivil_03` | Apenas WebFetch (Lei 8.078 compilada carregou, acentos truncados). Curl falha na conexão TLS (código 000, nos protocolos http/https) | HTML compilado | SIM (texto compilado com "Redação dada", "Revogado", vigência de artigo) | Curl nunca conecta; usar WebFetch. Acentos podem sair quebrados | 4 (via WebFetch) |
| INMETRO | `gov.br/inmetro` | Página inicial de Metrologia Legal abre (200), mas links profundos testados deram 404. Texto de Portaria 248/2008 só por WebSearch (legisweb, normasbrasil) | HTML | NÃO | Estrutura de URLs muda; sem acervo próprio testado | 2 (localizar via WebSearch e confirmar no DOU ou no site do Inmetro). Consulta de registro (`registro.inmetro.gov.br/consulta`) é ASP.NET com VIEWSTATE e foca produto certificado, não alimento: sem script (ver 3.7) |
| CVS-SP (Centro de Vigilância Sanitária do Estado de SP) | `cvs.saude.sp.gov.br` | WebSearch acha os PDFs (`/zip/PORTARIA CVS-5_2013.pdf`, `/up/E-PT-CVS-1_130125.pdf`). Raiz abre (571 bytes) | PDF | NÃO no PDF. Mas a busca indica que a Portaria CVS 5/2013 foi revogada por portaria de 2025 e há nova CVS 3 de 03/07/2026 (cadeia de revogação confirmada só por snippet) | Curl dá 403 nos PDFs; `www.cvs...` não resolve. Não testado WebFetch no PDF | 2 |
| VISA-MG (SES/MG) | `saude.mg.gov.br` | Home 200; `/vigilanciasanitaria` 404. Via WebSearch: Resolução SES 6.362/2018 (artesanal), 4.300/2014 (alvará) | HTML/PDF | NÃO | Sem busca de legislação testada | 2 |
| VISA-PR | `saude.pr.gov.br`, `vigilanciasanitaria.sesa.pr.gov.br` | Não funcionou | n/a | n/a | 403 e falha de conexão | 1 |
| VISA-RJ | `saude.rj.gov.br` | Home e `/vigilancia-sanitaria` abrem (200, pouco conteúdo) | HTML | NÃO | Sem acervo pesquisável testado | 1 |
| Codex Alimentarius | `codexalimentarius.org` (agora `codex.fao.org`) | Curl e WebFetch deram timeout/erro. WebSearch devolve cópias do CXS 1-1985 (FAO, revisão de 2024 sobre alérgenos) | PDF | n/a (referência internacional) | Site oficial inacessível nos testes | 2 (usar só como referência, com flag conferir) |
| ABNT | `abntcatalogo.com.br` | Home abre (200). URL de pesquisa que montei deu 404 | HTML | Catálogo mostra se a norma é "cancelada" (não testado) | Texto é pago. Nunca citar conteúdo | 2 (só código e título) |
| Agregadores (legisweb, normasbrasil, boaconta, FAO FAOLEX) | vários | WebSearch os retorna; abrem por curl (legisweb 200) | HTML | Alguns marcam "revogada" | Não são oficiais, podem estar desatualizados | 2 (apenas para achar o nome certo; nunca como fonte da citação) |

## 3. Receitas de consulta

### 3.1 Anvisa (RDC, texto integral e status)
Modelo de URL, trocando ano, número com 8 dígitos e tipo:
`https://anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=detalharAto&valorAno=2020&numeroAto=00000429&seqAto=000&tipo=RDC&orgao=RDC/DC/ANVISA/MS&codTipo=&desItem=&desItemFim=&cod_menu=1696&cod_modulo=134&pesquisa=`
No Bash: `curl -s -L -m 30 -A "Mozilla/5.0" "<url>"`. Decodificar como `latin1`, tirar tags, ler o primeiro rótulo ("Vigente", "Vigente com Alterações") e procurar "(Revogado pela" nos artigos. Resultado dos testes: RDC 429/2020 "Vigente com Alterações" (arts. 35 a 37 revogados pela RDC 729/2022); RDC 275/2002 "Vigente"; RDC 216/2004 "Vigente com Alterações".
Para IN da Anvisa: **`tipo=INM`** (verificado em 29/10/2026). O `orgao` muda conforme a época: `orgao=DC/ANVISA/MS` (ex.: IN 2020, 2023, 2024 abriram assim) ou `orgao=ANVISA/MS` (algumas IN de 2022). Ex.: `...valorAno=2020&numeroAto=00000075&seqAto=000&tipo=INM&orgao=DC/ANVISA/MS...`.
Outros tipos verificados: Portaria antiga da SVS/MS `tipo=POR&orgao=SVS/MS`; Portaria do Inmetro espelhada no AnvisaLegis `tipo=POR&orgao=INMETRO/ME`.
**`seqAto`**: quase sempre `000`, mas algumas RDC só abrem com `seqAto=002` (verificado: RDC 727/2022, RDC 724/2022 e RDC 715/2022). Se der "Este ato está sendo processado", tentar `001` e `002`.
**Diagnóstico:** a página com "Este ato está sendo processado" (≈460 bytes de texto) significa combinação de parâmetros errada, NÃO que a norma não existe. Variar nesta ordem: `seqAto` (000→002→001), `orgao` (RDC/DC/ANVISA/MS → DC/ANVISA/MS → ANVISA/MS → SVS/MS → RDC/ANVS), `tipo` (RDC, INM, POR, RES). Se nada abrir, achar a norma pelo DOU (3.3) e registrar o status como "não lido no AnvisaLegis".
**Ler o status no cabeçalho do ato** (bloco logo antes da ementa), não no menu da página: "Vigente", "Vigente com Alterações" ou "Revogado". Em "Vigente com Alterações", procurar no texto "(Revogado pela", "(Redação dada pela", "(Incluído pela" no artigo que vai ser citado.
Observação: o `WebSearch` com `site:anvisalegis.datalegis.net` NÃO retornou nada do domínio (testado com RDC 275/2002). Não usar como método principal.

### 3.2 BVS / Saúde Legis (texto de RDC/Portaria antiga)
`curl -s -L -A "Mozilla/5.0" https://bvsms.saude.gov.br/bvs/saudelegis/anvisa/2002/rdc0275_21_10_2002.html` (RDC 275/2002 carregou, título e ementa corretos, em UTF-8 com entidades HTML). Use para trecho citado, nunca para vigência.

### 3.3 DOU (norma nova, revogação publicada, texto original)
Busca (frase do título ou ementa, entre aspas, `sortType=1`):
`https://www.in.gov.br/consulta/-/buscar/dou?q=%22rotulagem+nutricional+dos+alimentos+embalados%22&s=do1&exactDate=all&sortType=1&delta=5`
Extrair o JSON: localizar `"jsonArray":[` até `</script>`, cortar até o último `]`, `json.loads`. Campos úteis: `title`, `pubDate`, `urlTitle`, `content`. Link do ato: `https://www.in.gov.br/web/dou/-/<urlTitle>`.
Teste: a busca devolveu RDC 429/2020 e IN 75/2020 (ambas 09/10/2020). A página da IN 75/2020 abriu (327 KB, texto na íntegra, "Seção 1, Página 113, Edição 195, 09/10/2020").
**Checar revogação/alteração posterior (receita geral):** buscar a citação por extenso como aparece em atos posteriores, ex. `"RDC nº 216, de 15 de setembro de 2004"` ou `"Instrução Normativa nº 75, de 8 de outubro de 2020"`, com `s=todos` e `sortType=0` (mais recentes primeiro). Abrir os atos mais novos e procurar "revoga"/"altera". Testado em 29/10/2026: a busca por `"revoga a Resolução da Diretoria Colegiada"` com `sortType=0` devolveu RDC de 2026 com texto de revogação no resumo.
Ferramentas prontas (stdlib): `regulatorio/ferramentas/dou_busca.py` (busca) e `dou_ato.py` (abre ato e lista trechos "revoga/altera"); `anvisalegis.py` (tenta seqAto/orgao/tipo sozinho e imprime status + notas de alteração).
Para "o que saiu recente": usar `sortType=0` e termos como "alimentos" com `s=do1`, depois filtrar por órgão (Anvisa, MAPA).

### 3.4 MAPA
1. Achar o PDF com `WebSearch` ("Portaria 368/1997 MAPA ..."), que devolveu `wikisda.agricultura.gov.br/dipoa_baselegal/port_368-1997_bpf.pdf`. Baixar com curl e extrair texto (PyMuPDF). Isso dá o texto de 1997, não o status.
2. Status: conferir no DOU se houve revogação posterior (busca pelo número e "revoga") e na página de legislação do MAPA (`gov.br/agricultura/.../produtos-animal/legislacao`, mostra data de atualização).
3. Bebidas, vinhos, vinagres: Cartilhão de Bebidas (IN 140/2024, 6ª ed., até 06/09/2025), localizado por `WebSearch`; conferir a data de corte antes de citar.
4. SISLEGIS: tentar apenas pelo navegador logado (Claude in Chrome), não por curl.

### 3.5 Planalto
`WebFetch` na URL canônica, p. ex. `https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm`. Pedir ao WebFetch o artigo exato e se há "Redação dada" ou "Revogado". Curl não conecta.

### 3.6 INMETRO, estaduais, Codex, ABNT
- Inmetro: `WebSearch` "Portaria Inmetro 248/2008 ..." para localizar; citar o link do DOU ou do Inmetro, e usar agregador só para achar o número. Marcar sempre "conferir" (consolidações recentes podem ter alterado).
- CVS-SP: `WebSearch` "Portaria CVS ..." devolve o PDF no domínio `cvs.saude.sp.gov.br`. Como curl toma 403, abrir pelo WebFetch/navegador. Marcar "conferir" e checar a cadeia de revogação (CVS 5/2013 foi substituída; há CVS 3/2026).
- MG, PR, RJ: sem acervo pesquisável confirmado. Procurar pelo número da resolução com `WebSearch` e abrir o PDF no domínio `saude.mg.gov.br` etc. Sempre "conferir".
- Codex: citar apenas como referência, com código CXS e ano; indicar que o site oficial não respondeu nos testes.
- ABNT: só código, título e situação do catálogo. Nunca citar texto.

### 3.7 Dados abertos: produto/empresa (Anvisa) e estabelecimento (MAPA), Inmetro, Ministério da Saúde

Testado ao vivo em 30/10/2026. 1 requisição por vez, User-Agent identificado, cache de 24 h em `%TEMP%\regulatorio-fran-cache` (variável `REGULATORIO_CACHE`). Sem login e sem contornar bloqueio.

**Anvisa: "este produto/empresa tem registro ou notificação?"**
```
python -I {{SQUAD_ROOT}}/regulatorio/ferramentas/anvisa_alimentos.py --produto "aroma natural" [--empresa "t"] [--cnpj 14dig] [--registro NUM] [--categoria "t"] [--situacao Ativo] [--n 20]
```
- Fonte: CSV de dados abertos da Anvisa. A saída diz a **data da carga** (ex.: 12/10/2026): resposta vale até ali.
- Ausência no CSV não prova irregularidade: grande parte dos alimentos é dispensada de registro (confira a norma vigente com `anvisalegis.py` antes de afirmar).
- Sempre acrescentar "conferir no site da Anvisa". O site `consultas.anvisa.gov.br` bloqueia ferramenta (403): caminho manual é o navegador.

**MAPA: estabelecimento com SIF / registro de estabelecimento de bebidas**
```
python -I {{SQUAD_ROOT}}/regulatorio/ferramentas/mapa_dados.py sif --razao "seara" --uf SC [--cnpj ..] [--nr-sif N] [--area carne] [--situacao A]
python -I {{SQUAD_ROOT}}/regulatorio/ferramentas/mapa_dados.py bebidas --razao "t" [--registro SP0013196] [--atividade "bebidas em geral"] [--status Ativo]
```
- `sif`: Estabelecimentos Registrados no SIF (SIGSIF). `bebidas`: SIPEAGRO, "Vinhos e Bebidas". Cerveja e suco entram em "BEBIDAS EM GERAL"; vinho em "VINHOS E DERIVADOS DA UVA E DO VINHO". Só estabelecimento, nunca produto. CNPJ mascarado em bebidas: busque por razão social ou nº de registro.
- A URL do CSV é achada pela API CKAN (`/api/3/action/package_show?id=servico-de-inspecao-federal-sif` ou `sipeagro`), então não depende do endereço do arquivo.
- Não imprime e-mail nem telefone das empresas.
- Fora de alcance (sem dado aberto): SISBI/e-Sisbi, SIE e SIM (estadual/municipal), SISLEGIS (login). Caminho manual: SFA do estado / órgão estadual de inspeção.

**Inmetro: sem acesso programático útil.** `registro.inmetro.gov.br/consulta` é formulário ASP.NET com VIEWSTATE (e foca produto certificado); `dados.gov.br` exige token (401). Para pré-medidos e conteúdo líquido: achar a Portaria por WebSearch, abrir no DOU (`dou_busca.py`/`dou_ato.py`) ou no site do Inmetro, marcar "conferir". Caminho manual: gov.br/inmetro, "Metrologia Legal".

**Ministério da Saúde: sem fonte nova.** O acervo útil continua sendo o BVS/Saúde Legis (receita 3.2, só texto, sem vigência) e o DOU. Não há API de normas; dados abertos do MS (OpenDataSUS) são de saúde assistencial, não de regulação de alimentos.

## 4. Ordem de consulta recomendada para o agente

1. Identificar órgão e tipo do ato. Se o usuário disser "IN 75" sem órgão, perguntar (Anvisa 2020 rotulagem, ou MAPA 2019 bebidas).
2. Anvisa: AnvisaLegis (3.1) para texto e status. MAPA/Saúde: DOU (3.3) para texto original e publicação.
3. Cruzar o status no DOU: procurar o título do ato mais "revoga" ou "altera" e ver os mais recentes.
4. Texto antigo sem status: BVS (3.2) ou wiki DIPOA (3.4), com flag conferir.
5. Lei e decreto: Planalto via WebFetch (3.5).
6. Medidas e quantidade (pré-medidos): Inmetro via WebSearch + confirmação no DOU, flag conferir.
7. Estadual: WebSearch no domínio da vigilância, flag conferir.
8. Se nenhuma fonte oficial devolveu o texto: responder "não encontrei na fonte oficial" e listar onde buscou. Não preencher com agregador nem com memória.

## 5. Formato de resposta sugerido (saída do agente)

- Norma: nome e número (órgão, ano)
- Link oficial usado
- Trecho citado entre aspas (curto)
- Status de vigência e de onde veio (ex.: "Vigente com Alterações, AnvisaLegis")
- Data da consulta
- Flag: `conferir` (obrigatória quando a fonte foi estadual, Inmetro, Codex, agregador, ou quando a vigência não foi lida numa fonte oficial)

## 6. Limites conhecidos

- Só os dados abertos (Anvisa CSV, MAPA CKAN) são fonte estruturada e estável; o resto é raspagem de HTML ou JSON embutido e pode quebrar. Dado aberto tem defasagem: sempre citar a data de carga/modificação.
- AnvisaLegis: a busca livre exige JS (não testada). Tipos validados: RDC, INM (IN), POR (SVS/MS e INMETRO/ME).
- SISLEGIS depende de sessão. Os PDFs da wiki DIPOA são cópias de 2023 sem status.
- A biblioteca temática de Alimentos da Anvisa não pôde ser lida (PDF 404). Data de atualização: não verificada. Não usar como compilado oficial.
- Biblioteca local do SIMPIA (D-biblioteca-normas.md) tem corte em fim de 2023/início de 2024 (defasagem de cerca de 2,5 anos). Serve como índice de nomes, não como fonte de vigência.
- Curl em Windows não conecta no Planalto e no Codex; usar WebFetch ou navegador.
- Acentos podem vir quebrados em ISO-8859-1; decodificar como latin1 antes de citar.
- Não testado: WebFetch em PDFs da CVS-SP; RDC 429 no BVS (404 no PDF); busca no AnvisaLegis por IN.

## 7. Benchmark local (SIMPIA, Fase 0) em 5 linhas

1. `FASE0.md` (rascunho de 01/10/2026): alvo de 90% de acerto com norma e página corretas em 28 perguntas, citadas nos itens 1.6 e 1.15 de `dados/A-docs-projeto.md`.
2. Passos: escolher 8 normas centrais, OCR/limpeza, indexar no Supabase com campo vigência, agente com citação, rodar as 28 perguntas, revisar gabarito com Fran e Giu porque as normas mudaram desde 2024.
3. O HANDOFF fala em "28 perguntas-teste com gabarito" como ativo do projeto, mas as perguntas em si NÃO estão em nenhum arquivo da pasta `simpia-reavaliacao` (busca por "28 perguntas" achou só menções em FASE0, HANDOFF, E, H e `plataforma-gestao/consolidacao/B-tecnico-foodchecker-simpia.md`).
4. O gabarito está desatualizado por definição (biblioteca com corte no fim de 2023); precisa de revisão da Fran/Giu antes de medir o agente.
5. O número 38,9% citado no pedido não aparece em `A-docs-projeto.md` nem em `FASE0.md`; origem a confirmar.
