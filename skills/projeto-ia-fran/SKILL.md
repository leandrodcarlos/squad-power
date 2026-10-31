---
name: projeto-ia-fran
description: Monta um PROJETO de IA fixo e reutilizável (Claude Projects, Gemini Gem ou GPT personalizado) para uma tarefa que a consultora de alimentos repete, com instruções fixas, modelo da entrega, base da área, exemplo bom e teste. Use quando ela disser "montar um projeto no Claude", "criar um GPT", "criar um Gem", "padronizar minhas entregas", "automatizar essa tarefa", "meu prompt não dá padrão", "demoro ajustando prompt" ou "automatizar minha rotina". Não escreve o relatório, a proposta ou o POP em si (isso é do agente do domínio); aqui se constrói a ferramenta que os produz sempre no mesmo padrão.
---

# Projeto de IA da consultora (método dos 3 arquivos)

Dor que resolve: falta de método e de padrão nas entregas, tempo perdido ajustando prompt, rotina manual.
Ideia: tarefa repetida vira um PROJETO fixo = **3 arquivos + instruções fixas**.

1. **Modelo da entrega** (a estrutura que a saída sempre segue)
2. **Base da área** (referências e legislação a anexar, tudo "conferir vigência")
3. **Exemplo bom** (um trabalho dela já feito, anonimizado)
4. **Instruções fixas** (objetivo, entradas, ordem, formato, o que nunca fazer, tom)

Funciona igual em Claude Projects, Gemini Gems e GPTs personalizados.

## Antes de começar
Leia `core/constituicao.md` e `core/voz-fran.md` do squad. Regra que vale em todo pacote: **não inventar norma, artigo, limite, prazo nem número; marcar `[conferir vigência]`**. Sem promessa sanitária. Sem dado de cliente (CNPJ, CPF, nome).

Se ela só quer um modelo pronto, ofereça os de `exemplos/` (relatorio-de-visita, proposta-comercial, pop) e pule a entrevista.

## Passo 1. Entrevista (máximo 6 perguntas, uma mensagem só, depois espere)
Mostre este menu e peça respostas curtas:
1. Qual tarefa você repete? (ex.: relatório de visita, proposta, POP, resposta a cliente)
2. Com que frequência? (por semana)
3. Quem recebe o resultado? (dono, equipe, fiscal, cliente final)
4. Cole um exemplo bom que você já fez (pode tirar os nomes depois).
5. Qual é a estrutura que você usa? (títulos, ordem, tamanho)
6. O que você mais corrige quando a IA erra?

Se faltar resposta, pergunte só o que falta uma vez; senão marque `[FALTA INFORMAR]`.

## Passo 2. Gerar o pacote
Preencha um JSON (veja `exemplos/*/respostas.json` como modelo de campos: titulo, tarefa, frequencia, destinatario, objetivo, entradas, passos, nunca, erros_comuns, tom, modelo_secoes, referencias, exemplo_bom, anonimizar, testes) e rode:

```
python "{{SQUAD_ROOT}}/skills/projeto-ia-fran/gerar_pacote.py" respostas.json --saida <pasta>
```

Gera 6 arquivos: `instrucoes.md`, `modelo-da-entrega.md`, `base-da-area.md`, `exemplo-bom.md`, `teste.md`, `COMO-USAR.md`. O script remove CNPJ, CPF, e-mail, telefone e os nomes listados em `anonimizar`, e recusa `instrucoes.md` acima de 8000 caracteres.

Regras ao preencher:
- `instrucoes` na voz da consultora (colega para colega, direto), objetivo antes da técnica.
- Entradas: o que a IA precisa receber; se faltar, ela pede antes de produzir.
- `referencias`: só documentos oficiais que ela baixa; cite o NOME da norma-base com "(conferir vigente)". Nunca artigo, item, temperatura ou prazo.
- Entrega final é rascunho: a consultora revisa.
- Dados de formalização da consultora (MEI/ME, ART, contrato) não são norma sanitária; feche com "confirme com seu contador / conselho profissional".

## Passo 3. COMO-USAR (1 página)
O gerador já escreve o passo a passo de Claude Projects, Gemini Gems e GPTs, com o aviso "nomes de botões podem mudar". Entregue a pasta e diga qual arquivo vai em qual campo.

## Passo 4. Iterar (simular antes de entregar)
1. Para cada entrada de `teste.md`, simule a resposta que as instruções produziriam, seguindo-as ao pé da letra.
2. Compare com a lista "a resposta boa precisa ter". Ache o furo (título faltando, número inventado, nome vazado, pergunta que deveria ter sido feita).
3. Corrija UMA coisa por vez nas instruções ou no modelo, regere e repita até os 3 testes mais o teste fixo passarem.
4. Rode `python "{{SQUAD_ROOT}}/skills/projeto-ia-fran/gerar_pacote.py" --validar <pasta>`: confere os 6 arquivos, limite de 8000 caracteres, regra do conferir e ausência de CNPJ/CPF/e-mail.
5. Peça que ela use 3 vezes de verdade; cada correção manual vira uma linha em "Nunca faça" ou "Erros que eu mais corrijo".

## Fecho
Termine com o próximo passo concreto: "hoje, crie o projeto na plataforma que você já usa e rode o teste 1. Depois você me conta como saiu, tá?"

## Kit de projetos prontos
`exemplos/relatorio-de-visita/`, `exemplos/proposta-comercial/`, `exemplos/pop/`: cada um completo, usável como está. Base do kit da masterclass.
