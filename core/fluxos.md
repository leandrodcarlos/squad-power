# Fluxos prontos do Squad Power

Comando nomeado, agentes em ordem, trava de qualidade no fim. Cada passo recebe a saída do anterior. A `revisora-fran` é o último passo antes de a entrega ir ao cliente.

| Comando | Quando | Passos (nesta ordem) | Entrega |
|---|---|---|---|
| `*visita` | tem áudio, foto, anotação ou checklist de visita | 1. visita-fran (transcreve, organiza, gera relatório) 2. regulatorio-fran só se houver dúvida de norma 3. revisora-fran | relatório .docx + mensagem de WhatsApp |
| `*proposta` | vai orçar um serviço | 1. val-fran (valor e proposta) 2. camila-fran (roteiro da reunião e objeção de preço, coerente com a proposta) 3. revisora-fran | proposta .docx para o cliente + roteiro .docx só para ela |
| `*bpf` | cliente precisa de Manual de BPF, POP ou checklist | 1. bpf-fran (documento .docx) 2. regulatorio-fran confere as normas citadas 3. revisora-fran | documento técnico |
| `*norma` | "é permitido?", rotulagem, vigência | regulatorio-fran | norma, artigo, vigência, link oficial |
| `*site` | quer site ou proposta com visual caprichado | 1. isa-fran (texto e posicionamento) ou val-fran (valores da proposta) 2. design-fran (arquivo final) 3. revisora-fran | .html, .docx, .pptx ou .pdf |
| `*comecar` | consultora nova ou reposicionando | 1. orquestradora-fran (fase e trava) 2. aurora-fran (nicho) 3. helena-fran (meta dos 90 dias) | plano dos próximos 90 dias |
| `*prospectar` | quer clientes | 1. isa-fran (conteúdo e perfil) 2. camila-fran (contatos da semana, script, follow-up) | plano semanal + scripts |
| `*padronizar` | repete a mesma tarefa e quer padrão | sofia-fran com a skill projeto-ia-fran | projeto Claude, Gem ou GPT |
| `*revisar` | tem texto pronto para conferir | revisora-fran | lista de ajustes por gravidade |

## Antes de delegar
- Falta o dado que muda o resultado (tipo de empresa, horas, valor, data)? Peça só esse dado, uma vez.
- Não passe dado pessoal de cliente (CNPJ, CPF, nome de pessoa) entre agentes: use [CLIENTE].
- Artigo, item, limite ou prazo de norma só vem do regulatorio-fran. Nome de norma-base pode aparecer com "(conferir vigente)", como manda a constituição §3.

## Depois da revisora
A revisora é o último filtro antes do arquivo final, não o fim do fluxo.
1. Veredito BLOQUEADO ou AJUSTAR: chame de novo o agente que gerou o arquivo, com a lista de correções, para ele regenerar. Use só agentes `*-fran`.
2. Mande a nova versão à revisora uma vez, no máximo. Continuou com bloqueio: entregue dizendo o que falta decidir, sem chamar de pronto.
3. Mostre o veredito final e o que mudou em até 5 linhas.
4. Quem coordena nunca edita o arquivo direto, nem correção pequena. Só o agente que gerou mexe nele.

## Quando ela disser "sem me perguntar nada"
Não faça pergunta no fim. Decida pelo que a base recomenda, marque `[FALTA INFORMAR: ...]` no que não dá para decidir e liste como pendência.

## Critério de pronto
1. Cada passo rodou e a saída foi ao seguinte.
2. Arquivo prometido existe na pasta (.docx, .html). Se não saiu, diga isso.
3. A revisora-fran revisou e as correções dela estão no arquivo final (exceto `*norma`).
4. O que depende de norma tem link oficial ou `[conferir vigência]`.
5. A resposta traz "Decisões suas antes de enviar" (desconto, parcelamento, bônus, validade, opções, com valor) e "Falta preencher" (cada marca de cada arquivo entregue, inclusive [CLIENTE] e [EMPRESA]). Monte essa lista pedindo ao agente que gerou o arquivo, que relê o arquivo final; não escreva de memória o que tem ou não tem nele.
6. A resposta termina com "Próximo passo:" e diz que é rascunho para a consultora conferir.

## Memória
Com o plugin claude-mem instalado, o contexto das conversas fica salvo neste computador. Ainda assim, não digite CPF, CNPJ ou dado sensível de cliente: o que entra na conversa pode entrar na memória.
