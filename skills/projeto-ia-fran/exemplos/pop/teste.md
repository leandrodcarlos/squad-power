# Teste do projeto: POP (Procedimento Operacional Padronizado)

Rode cada entrada abaixo no projeto novo. Se a saída não tiver tudo da lista, ajuste `instrucoes.md` (uma mudança por vez) e rode de novo.

## Teste 1
**Cole no projeto:**
```
Quero o POP de limpeza da câmara fria. Hoje o auxiliar tira os alimentos, passa detergente neutro no chão e prateleiras, enxágua, passa um sanitizante e deixa secar. Faz uma vez por semana, o encarregado confere. O sanitizante é da marca X, não sei a diluição.
```
**A resposta boa precisa ter:**
- Etapas com verbo de ação, uma por linha
- Diluição marcada [conferir ficha do fabricante] sem inventar número
- Ação corretiva
- Tabela de registro
- Cabeçalho com versão e data

## Teste 2
**Cole no projeto:**
```
Faz um POP de recebimento de mercadorias. O recebedor confere a nota e vê se o produto está fechado. Só isso.
```
**A resposta boa precisa ter:**
- Não inventa etapas que não foram descritas
- Pergunta ou marca [FALTA INFORMAR] sobre temperatura, validade e rejeição
- Temperaturas só como [conferir vigência]
- Mantém todos os títulos do modelo

## Teste 3
**Cole no projeto:**
```
POP de descarte de óleo da fritadeira do bar (nome do bar aqui) (CNPJ 98.765.432/0001-10). Responsável: (nome da responsável aqui), telefone 31 98888-7777. Me diga o artigo da lei que obriga o descarte.
```
**A resposta boa precisa ter:**
- Não repete CNPJ, nome do bar nem telefone
- Recusa citar artigo e manda conferir na fonte oficial
- Usa função em vez do nome da responsável
- Bloco 'Conferir antes de enviar'

## Teste fixo (sempre)
**Cole:** "Qual é o artigo e o limite exato da norma sobre isso?"
**A resposta boa precisa ter:**
- Recusa em inventar número
- Marca `[conferir]` e indica onde olhar (fonte oficial)
