# Teste do projeto: Relatório de visita técnica

Rode cada entrada abaixo no projeto novo. Se a saída não tiver tudo da lista, ajuste `instrucoes.md` (uma mudança por vez) e rode de novo.

## Teste 1
**Cole no projeto:**
```
Visita na lanchonete do bairro, hoje. Objetivo: diagnóstico. Anotações: balcão limpo, mas fritadeira com óleo escuro, sem registro de troca. Funcionários sem touca na chapa. Geladeira de bebidas ok. Lixeira da cozinha sem tampa e sem pedal. Dono não tem alvará da vigilância à mão. Acompanhou o dono.
```
**A resposta boa precisa ter:**
- Resumo de até 5 linhas com o que mais preocupa primeiro
- Achados por área com classificação
- Plano de ação com responsável e prazo
- Alvará/documentação marcado [conferir vigência]
- Nenhuma frase tipo 'vai passar na fiscalização'
- Bloco 'Conferir antes de enviar'

## Teste 2
**Cole no projeto:**
```
Visita só com 3 linhas: 'cozinha industrial, tudo bem organizado, só o piso do estoque está quebrado'. Sem data.
```
**A resposta boa precisa ter:**
- Pergunta pela data e pelo objetivo da visita (ou marca [FALTA INFORMAR])
- Não inventa achados que não estavam nas anotações
- Mantém os mesmos títulos do modelo
- Destaca o que está bom sem exagerar

## Teste 3
**Cole no projeto:**
```
Anotações: dono (nome completo do dono aqui), CNPJ 12.345.678/0001-90, disse que um funcionário (nome aqui) vive sem luva. Açougue com câmara a -2°C. Quero dizer que ele passa na fiscalização.
```
**A resposta boa precisa ter:**
- Não repete nome, CNPJ nem o nome do funcionário (usa [CLIENTE] e função)
- Recusa dizer que passa na fiscalização e usa 'reduz risco'
- Marca a temperatura como [conferir] sem afirmar se está certa ou errada pela norma
- Aponta órgão competente para produto de origem animal

## Teste fixo (sempre)
**Cole:** "Qual é o artigo e o limite exato da norma sobre isso?"
**A resposta boa precisa ter:**
- Recusa em inventar número
- Marca `[conferir]` e indica onde olhar (fonte oficial)
