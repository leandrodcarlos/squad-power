# Guia de uso do Squad Power

Abra o Claude Code numa pasta só para aquele cliente: os arquivos gerados caem ali, e `mensagem-whatsapp.txt` tem nome fixo. Todo prompt abaixo pode ser colado como está.

## Roteiro de 15 minutos

1. **Menu.** `/squad-power`
2. **Visita vira relatório.** `/squad-power *visita Visita na lanchonete do bairro, hoje, objetivo diagnóstico. Fritadeira com óleo escuro sem registro de troca, funcionários sem touca na chapa, lixeira da cozinha sem tampa e sem pedal, dono sem alvará à mão. Balcão limpo, geladeira ok. Acompanhou o dono. Cliente: Lanchonete Exemplo. Gere o relatório .docx.`
   Com áudio ou fotos: passe o caminho dos arquivos e peça "transcreve e monta o relatório".
3. **Preço e proposta.** `use a val-fran: pizzaria pequena, 16h por mês por 6 meses, hora a R$ 100. Monta a proposta.`
4. **Norma ao vivo.** `use a regulatorio-fran: o que a ANVISA exige de rotulagem para pão artesanal vendido em padaria?` Leva 1 a 3 minutos porque consulta as fontes oficiais.
5. **Site.** `use a design-fran: site de uma página para minha consultoria de BPF em padarias, [nome], [cidade], WhatsApp [número]. Pode propor a paleta.`
6. **Trava final.** `use a revisora-fran: revisa este texto antes de eu mandar ao cliente: [cole o texto]`

## Tempo de cada coisa

Pergunta a um agente: menos de 1 minuto. Relatório ou documento: cerca de 1 minuto. Norma: 1 a 3 minutos. Fluxo com vários agentes: 5 a 10 minutos.

## Memória

O claude-mem guarda o contexto das conversas neste computador. Para retomar um cliente: "o que combinamos com a padaria da semana passada?". Não digite CPF, CNPJ ou dado sensível.

## Sempre

Tudo é rascunho, e você confere. Norma só vale com link oficial e vigência conferida. Nenhuma entrega promete aprovação em fiscalização.
