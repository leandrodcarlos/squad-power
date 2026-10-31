# Manual do Squad Power

Time de agentes de IA para consultoras de alimentos, no método da Fran D'Carlos. Roda dentro do Claude Code.

**Regra principal: tudo o que o squad entrega é rascunho. Você confere antes de mandar ao cliente.**

## 1. Comece aqui

1. Abra o Claude Code numa pasta só para aquele cliente. Os arquivos gerados caem nela.
2. Digite `/squad-power`. Aparece o menu.
3. Escolha um comando e mande os dados junto:

```text
/squad-power *visita Visita na lanchonete do bairro, hoje, objetivo diagnóstico. Fritadeira com óleo escuro sem registro de troca, funcionários sem touca na chapa, lixeira sem tampa. Balcão limpo, geladeira ok. Cliente: Lanchonete Exemplo. Gere o relatório .docx.
```

4. Leia no fim da resposta as listas "Decisões suas antes de enviar" e "Falta preencher". Resolva cada item.
5. Abra o arquivo, confira e só então envie.

## 2. Como o squad é organizado

| Peça | O que é | Quantas | Como você usa |
|---|---|---|---|
| Coordenação | A skill `/squad-power`. Mostra o menu, escolhe a ordem e chama os agentes | 1 | Digita `/squad-power` |
| Agentes | Especialistas, cada um com um assunto e uma base de conhecimento | 12 | "use a val-fran: ..." ou por um comando |
| Skills | Ferramentas que geram arquivo ou transcrevem áudio | 4, além da coordenação | Os agentes usam sozinhos |
| Base | Conteúdo do método da Fran, em 9 áreas e 59 arquivos | 59 | Os agentes consultam sozinhos |
| Plugins | Complementos de memória, design e documentos | 3 | Entram no instalador |

### Agente e subagente: qual a diferença?

No Squad Power, os 12 agentes funcionam como **subagentes** do Claude Code. A conversa principal é quem dá o pedido, e cada subagente trabalha separado e devolve o resultado.

```text
Você
 └─ Conversa principal (coordena com /squad-power)
     ├─ visita-fran       gera o relatório
     ├─ regulatorio-fran  confere a norma, se houver dúvida
     └─ revisora-fran     revisa antes de entregar
```

O que isso muda para você:

- **O agente não vê a conversa.** Ele só recebe o que foi passado no pedido. Mande os dados juntos, ou repita o que importa.
- **A ordem é fixa nos comandos.** A saída de um agente vai para o próximo.
- **Só quem gerou o arquivo mexe nele.** A revisora aponta, e o agente de origem corrige.
- **Todos rodam no modelo Sonnet.** Ele passou nos testes do squad e gasta menos do limite do seu plano do que o Opus.

## 3. Os comandos

Use assim: `/squad-power *comando seu pedido e seus dados`.

| Comando | Quando usar | Ordem dos agentes | O que você recebe |
|---|---|---|---|
| `*visita` | Tem áudio, foto, anotação ou checklist de visita | visita-fran → regulatorio-fran, se houver dúvida de norma → revisora-fran | Relatório `.docx`, mensagem de WhatsApp e lista de conferência |
| `*proposta` | Vai orçar um serviço | val-fran → camila-fran → revisora-fran | Proposta `.docx` para o cliente e roteiro `.docx` só para você |
| `*bpf` | Precisa de Manual de BPF, POP ou checklist | bpf-fran → regulatorio-fran → revisora-fran | Documento técnico `.docx` |
| `*norma` | "É permitido?", rotulagem, vigência | regulatorio-fran | Norma, artigo, vigência, link oficial e trecho |
| `*site` | Quer site ou proposta com visual caprichado | isa-fran ou val-fran → design-fran → revisora-fran | `.html`, `.docx`, `.pptx` ou `.pdf` |
| `*comecar` | Está começando ou se reposicionando | orquestradora-fran → aurora-fran → helena-fran | Plano dos próximos 90 dias |
| `*prospectar` | Quer conseguir clientes | isa-fran → camila-fran | Plano semanal e scripts |
| `*padronizar` | Repete uma tarefa e quer um padrão | sofia-fran com a skill projeto-ia-fran | Projeto para Claude, Gemini ou ChatGPT |
| `*revisar` | Tem um texto pronto para conferir | revisora-fran | Lista de ajustes por gravidade |

### Exemplos prontos

```text
/squad-power *proposta Pizzaria pequena, 16h por mês por 6 meses, hora a R$ 100. Monta a proposta e o roteiro da reunião.
```

```text
/squad-power *bpf POP de recebimento de mercadorias para padaria pequena, 6 funcionários, sem POP hoje.
```

```text
/squad-power *norma O que a ANVISA exige de rotulagem para pão artesanal vendido em padaria?
```

```text
/squad-power *site Site de uma página para minha consultoria de BPF em padarias, [nome], [cidade], WhatsApp [número]. Pode propor a paleta.
```

```text
/squad-power *comecar Sou nutricionista, nunca atendi como consultora e tenho 10 horas por semana.
```

```text
/squad-power *prospectar Atendo padarias na minha cidade e quero fechar 2 clientes novos neste mês.
```

```text
/squad-power *padronizar Faço 4 relatórios de visita por semana e cada um sai de um jeito.
```

```text
/squad-power *revisar Confere este texto antes de eu mandar ao cliente: [cole o texto]
```

### Sem comando

Escreva o que precisa depois de `/squad-power`. O squad identifica o fluxo pela intenção. Dúvida de carreira vai para a mentora.

### Sem me perguntar nada

Escreva "sem me perguntar nada" no pedido. O squad decide pelo que a base recomenda, marca `[FALTA INFORMAR: ...]` no que não dá para decidir e lista as pendências.

## 4. Os 12 agentes

Para chamar um direto: `use a val-fran: quanto cobro por um manual de BPF?`

Com pergunta concreta, o agente responde na hora. Sem pergunta, ele pode mostrar um menu de opções. Para gerar um documento, ele faz até 5 perguntas, uma por vez.

### Negócio da consultora

| Agente | Nome | O que faz | Exemplo de pedido |
|---|---|---|---|
| `orquestradora-fran` | Mentora | Entende sua fase, responde como mentora e indica o próximo agente | "use a orquestradora-fran: por onde começo?" |
| `aurora-fran` | Aurora | Nicho, missão, visão, valores e identidade | "use a aurora-fran: me ajuda a definir meu nicho" |
| `helena-fran` | Helena | Metas, plano anual, SWOT, 5W2H, indicadores, delegar e contratar | "use a helena-fran: como transformo minha meta em clientes por mês?" |
| `sofia-fran` | Sofia | Caixa, ponto de equilíbrio, processos, contratação, contrato, MEI e cobrança | "use a sofia-fran: quando vale contratar alguém?" |

### Vendas e marketing

| Agente | Nome | O que faz | Exemplo de pedido |
|---|---|---|---|
| `val-fran` | Val | Preço, hora técnica, pacote e proposta `.docx` | "use a val-fran: quanto cobro por um manual de BPF?" |
| `camila-fran` | Camila | Prospecção, roteiro de reunião, objeções e follow-up | "use a camila-fran: o cliente disse que está caro, o que respondo?" |
| `isa-fran` | Isa | Conteúdo, calendário, Reels, bio, Instagram e LinkedIn | "use a isa-fran: monta meu calendário do mês" |
| `design-fran` | Dani | Site de uma página, proposta visual, apresentação e carrossel | "use a design-fran: transforma esta proposta numa apresentação" |

### Parte técnica

| Agente | Nome | O que faz | Exemplo de pedido |
|---|---|---|---|
| `bpf-fran` | Bia | Manual de BPF, POP, checklist, ficha técnica, PAC, planilha, treinamento e o negócio de BPF | "use a bpf-fran: faz um POP de higienização" |
| `visita-fran` | Vera | Transforma visita ou auditoria em relatório e plano de ação | "use a visita-fran: organiza este checklist em relatório" |
| `regulatorio-fran` | Rê | Consulta a norma ao vivo em fontes oficiais, com artigo, vigência e link | "use a regulatorio-fran: este produto precisa de registro?" |
| `revisora-fran` | Rita | Última conferência: dá o veredito e aponta o que corrigir, sem alterar o arquivo | "use a revisora-fran: revisa este texto" |

### O que a Rê consulta

ANVISA, MAPA, Diário Oficial, Planalto, INMETRO, Ministério da Saúde e vigilâncias estaduais e municipais. Sobre ABNT, cita só código e título. O Codex entra só como referência internacional.

Ela também verifica se um produto ou empresa consta nos dados abertos da ANVISA e se um estabelecimento aparece nos dados do MAPA (SIF e bebidas). Não constar nos dados da ANVISA não prova irregularidade, porque muito alimento é dispensado de registro.

### O que a Rita confere

1. Norma citada sem fonte conferida.
2. Promessa de aprovação em fiscalização.
3. Voz da Fran.
4. Próximo passo para o cliente.
5. Dado pessoal exposto.
6. Fato que você não informou.
7. Promessa disfarçada, como "evita autuação".
8. Coerência entre arquivos e conta interna visível ao cliente.
9. Recado interno dentro do arquivo do cliente.

O veredito é `BLOQUEADO`, `AJUSTAR` ou `PODE ENVIAR`. Nos fluxos, o agente corrige e a revisora olha de novo uma vez. Se ainda houver bloqueio, a entrega vem dizendo o que falta decidir.

## 5. As skills

| Skill | O que faz | Quem usa | Precisa de |
|---|---|---|---|
| `squad-power` | Menu e coordenação dos fluxos | Você | Nada além do squad |
| `relatorio-visita-fran` | Fotos, áudio e anotações viram relatório `.docx`, mensagem de WhatsApp e `revisao-conferir.txt`. Também faz relatório de auditoria (ISO 22000, FSSC, APPCC) | visita-fran | Python |
| `transcrever-audio-fran` | Transcreve áudio e vídeo no seu computador, sem enviar o áudio para a internet. Aceita `.m4a`, `.ogg`, `.opus`, `.mp3`, `.wav` e `.mp4` | visita-fran | Python e ffmpeg. Baixa o modelo no primeiro uso |
| `documento-tecnico-fran` | Gera POP, Manual de BPF, ficha técnica, PAC e planilha `.docx`. Usa o seu modelo, se você mandar | bpf-fran | Python |
| `projeto-ia-fran` | Monta um projeto fixo para uma tarefa repetida | sofia-fran | Python |

**Dica de transcrição:** o áudio pode errar termo técnico, nome e número de norma. Revise o texto antes de usar.

**Atenção à sigla PAC:** em documentos, é programa de autocontrole. Na base da Fran, também é o Programa de Aceleração em Consultoria.

## 6. Os plugins

| Plugin | O que faz | Usado por |
|---|---|---|
| claude-mem | Guarda o contexto das conversas no seu computador. Exemplo: "o que combinamos com a padaria da semana passada?" | Você |
| ui-ux-pro-max | Estilos, paletas e fontes para sites | design-fran |
| document-skills | Word, PowerPoint, Excel e PDF | design-fran |

## 7. As regras que o squad segue

- **Método primeiro:** responde pela base da Fran. O que vem de fora aparece como "(orientação geral, não é do método)".
- **Fonte:** o que vem de aula traz `(Fonte: curso › módulo › aula)`.
- **Norma:** artigo, limite, temperatura e prazo legal só vêm da `regulatorio-fran`, lidos na hora. Os outros agentes citam no máximo o nome da norma-base, com "(conferir vigente)".
- **Fiscalização:** nenhum agente promete aprovação. O squad fala em "reduz risco" e "deixa preparada".
- **Só o que você informou:** o que faltar vira `[FALTA INFORMAR: ...]`.
- **Próximo passo:** toda resposta termina com uma ação para hoje.
- **Dados de cliente:** nos fluxos, nomes viram `[CLIENTE]` e `[EMPRESA]`. Preencha antes de enviar.
- **Seus arquivos:** nenhum agente apaga, move ou renomeia arquivo que não criou na tarefa.

## 8. Antes de enviar ao cliente

- [ ] Li o arquivo inteiro.
- [ ] Resolvi "Decisões suas antes de enviar".
- [ ] Preenchi tudo de "Falta preencher" e procurei `[FALTA INFORMAR`, `[CLIENTE]`, `[EMPRESA]` e `⚠️ conferir` no arquivo.
- [ ] No relatório de visita, conferi o `revisao-conferir.txt` e tirei qualquer "(sugestão)" ao lado de risco ou prazo.
- [ ] Abri cada link de norma e conferi a vigência.
- [ ] A entrega não promete aprovação.

**Dois cuidados conhecidos:**

- O relatório pode sair com "Risco (sugestão)" no arquivo do cliente. Tire antes de enviar.
- A revisora às vezes não relê a última versão. Quando isso acontece, a resposta avisa. Nesse caso, peça: `use a revisora-fran: revisa o arquivo final [caminho]`.

## 9. Quanto tempo leva

| Tarefa | Tempo aproximado |
|---|---|
| Pergunta a um agente | Menos de 1 minuto |
| Relatório ou documento, chamando o agente direto | Cerca de 1 minuto |
| Norma | 1 a 3 minutos |
| Fluxo com vários agentes | 5 a 10 minutos |

Fluxos gastam mais do limite do seu plano Claude. Para uma dúvida simples, chame o agente direto.

## 10. Instalar, atualizar e personalizar

**Você precisa de** Claude Code com plano Claude ativo. Para arquivos `.docx`, precisa de Python. Para áudio, também de ffmpeg.

**Windows:** abra o PowerShell na pasta do squad e rode:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

**Mac:** abra o Terminal na pasta do squad e rode:

```bash
bash install.sh
```

Depois, feche e abra o Claude Code.

**Não mova nem apague a pasta do squad.** Os agentes leem a base dali. Se mudar de lugar, rode o instalador de novo.

**Atualizar:** troque os arquivos da pasta pela versão nova e rode o instalador.

**Personalizar:** os agentes instalados ficam em `.claude\agents\` na sua pasta de usuário, e você pode editar a cópia do seu computador. **O instalador regrava esses arquivos, então uma atualização apaga o que você mudou.** Guarde uma cópia das suas alterações antes de atualizar. Para mudar só uma entrega, é mais simples dizer no pedido: "use meu modelo [arquivo]" ou "minha hora técnica é R$ X".

## 11. Sem Claude Code

A pasta `skills/projeto-ia-fran/exemplos/` tem kits prontos para Claude Projects, Gemini Gems e GPTs: relatório de visita, proposta comercial e POP. Cada kit tem um `COMO-USAR.md`.

## 12. Limites

- O squad não substitui sua responsabilidade técnica.
- Sites só são publicados se você pedir. A entrega padrão é o arquivo.
- O que você digita vai para o serviço de IA e pode entrar na memória local. Não digite CPF, CNPJ nem dado sensível.
- A instalação no Mac ainda não foi testada em um Mac real.
- Os kits para Claude Projects, Gemini e ChatGPT ainda não foram testados nas telas desses serviços.
- O conteúdo é exclusivo da comunidade. Não repasse.

## 13. Problemas comuns

| Sintoma | O que fazer |
|---|---|
| `/squad-power` não aparece | Feche e abra o Claude Code. Se continuar, rode o instalador de novo |
| `.docx` não sai | Rode `python -m pip install -r requirements.txt` na pasta do squad |
| Áudio não transcreve | Instale o ffmpeg. No Windows: `winget install Gyan.FFmpeg` |
| PowerShell bloqueia o script | Use o comando com `-ExecutionPolicy Bypass` da seção 10 |
| Agente não acha a base | A pasta mudou de lugar. Rode o instalador de novo |
| Agente pergunta o que você já disse | Ele não vê a conversa. Repita os dados no pedido |
| Arquivo prometido não apareceu | Confira a pasta aberta no Claude Code. A resposta deve avisar se o arquivo não saiu |
| `mensagem-whatsapp.txt` foi substituído | O nome é fixo. Use uma pasta por cliente |
