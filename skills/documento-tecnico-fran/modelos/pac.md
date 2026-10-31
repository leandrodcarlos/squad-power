# Esqueleto: PAC (Programa de Autocontrole)

ATENÇÃO: não há modelo de PAC nos materiais do curso lidos. Na base da Fran, "PAC" também é a sigla do Programa de Aceleração em Consultoria, outro assunto. Aqui PAC = programa de autocontrole de estabelecimentos de produtos de origem animal (inspeção do MAPA). Esqueleto GERAL; o conteúdo exigido deve ser conferido via `regulatorio-fran` (MAPA, DOU). Se a consultora tiver modelo próprio, usar a estrutura DELA. Tipo no gerador: `pac`.

Perguntar antes: é produto de origem animal sob inspeção (SIF/SIE/SIM)? Se não for, provavelmente o que o cliente precisa é MBP + POPs.

## Seções (esqueleto geral)
1. **Identificação do estabelecimento** e do responsável técnico.
2. **Descrição do estabelecimento e dos produtos**: fluxo de produção, fluxograma, layout.
3. **Elementos do programa**: uma subseção para cada elemento de controle exigido pela norma vigente. Lista e nomes: ⚠️ referência a conferir (não preencher de memória).
4. Para cada elemento: objetivo · responsável · procedimento · monitoramento (o quê, como, quando, quem) · critérios e limites ⚠️ conferir · ação corretiva · verificação · registro (ficha).
5. **Treinamento da equipe** envolvida.
6. **Verificação do programa e revisão**: periodicidade proposta (⚠️ conferir se há exigência).
7. **Anexos**: fichas de registro, laudos, fluxograma.

## Regra
Todo critério numérico, prazo e lista de elementos do PAC só entra sem flag se vier de consulta feita ao vivo (campo `fonte_conferida` da seção). Caso contrário o gerador marca.
