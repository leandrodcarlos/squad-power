# Como usar este pacote (1 página)

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
