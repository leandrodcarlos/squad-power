---
name: relatorio-visita-fran
description: Transforma o material da visita técnica (fotos, áudios, anotações e/ou checklist preenchido) em relatório padrão com não conformidades, plano de ação priorizado e mensagem curta de WhatsApp para o cliente, no método da Fran D'Carlos. Também faz relatório de auditoria (ISO 22000, FSSC, APPCC) com mapeamento de cláusulas "a conferir". Use quando a consultora pedir "relatório de visita", "relatório da visita técnica", "fotos da visita", "áudio da visita", "não conformidades", "plano de ação do cliente" ou "relatório de auditoria". Objetivo - sair do cliente com o relatório pronto.
---

# Relatório de visita (Squad Power)

Entrada: fotos (.jpg/.png), áudios, anotações digitadas e/ou checklist preenchido.
Saída: `.docx` do relatório, `mensagem-whatsapp.txt` e `revisao-conferir.txt` (lista de conferência só para a consultora).

Método e termos: `base/visita/frameworks.md` (NC01, NC02..., responsável pessoa, prazo, coluna "Feito?" para o cliente, pontos positivos primeiro). Regras: `core/constituicao.md` (§3 norma, §4 sem promessa sanitária) e voz em `core/voz-fran.md`.

## Passos

1. **Coletar entradas.** Peça só o que falta, no máximo 3 perguntas: (a) cliente/estabelecimento, (b) data da visita, (c) tipo: visita ou auditoria. Não pergunte o que já está nos arquivos. CNPJ/CPF do cliente: não pedir (§7).
2. **Transcrever áudio.** Para cada áudio: `python "{{SQUAD_ROOT}}/skills/transcrever-audio-fran/transcrever.py" "<audio>"`. Leia o `.txt` gerado. O áudio fica no computador; não suba em serviço externo.
3. **Olhar cada foto** (Read mostra a imagem). Descreva só o que está visível: o que se vê, em qual área, o que está em desacordo ou conforme. Nunca deduza além da imagem (causa, temperatura que não aparece, quem fez). Se a foto não permite concluir, escreva "não dá para concluir pela foto" e pergunte à consultora.
4. **Consolidar as NCs.** Cruze foto + transcrição + notas. Uma NC por achado, descrita uma vez só. Para cada uma: área, achado, foto, risco (alto/medio/baixo, avaliação da consultora a partir do que viu), ação corretiva, responsável (pessoa, não setor), prazo. Se a ação for serviço da consultora (treinamento, POP, manual), escreva de modo que o cliente perceba a necessidade. Inclua `pontos_positivos`: a Fran começa por eles.
5. **Revisão obrigatória, marque ⚠️ conferir.** Todo número (temperatura, prazo, medida) e toda referência normativa. O gerador faz isso sozinho no documento e em `revisao-conferir.txt`. Atenção: o Whisper pode transformar "9 graus" em "9º" ou trocar números; confirme com a consultora o valor que ela anotou.
   - **Referência/requisito:** para citar norma, artigo, limite ou prazo legal, delegue ao agente `regulatorio-fran` (consulta ao vivo nas fontes oficiais). Só com essa consulta use `referencia_status: "conferida"`. Sem consulta ao vivo: deixe a referência vazia ou só com o nome da norma-base "(conferir vigente)" e `referencia_status: "a conferir"`. Nunca de memória, nunca cite artigo ou limite (constituição §3).
   - Limites ditos em áudio (ex.: "o limite é 5º") são fala da consultora, não fonte: não vão como fato.
6. **Gerar os entregáveis.** Monte o JSON (schema abaixo) numa pasta do cliente, e rode:
   ```
   python "{{SQUAD_ROOT}}/skills/relatorio-visita-fran/gerar_relatorio.py" visita.json [--saida PASTA] [--nome relatorio-AAAA-MM-DD]
   ```
   Requer `pip install python-docx` (fotos: Pillow, já vem junto como dependência quando há imagens). O `.docx` traz capa, resumo executivo (contagem por risco), tabela de NCs com foto ao lado, plano de ação ordenado por risco e prazo, rodapé "cliente · relatório de visita · data". Sem menção a ferramenta ou a quem gerou.
7. **Passada final com a revisora-fran** (`agents/revisora-fran.md`): norma citada sem conferência, promessa sanitária, voz, próximo passo, dado pessoal. Corrija o JSON e gere de novo até "PODE ENVIAR". Depois a consultora confere `revisao-conferir.txt` e tira os avisos ⚠️ do `.docx` já conferidos.

Termine sempre com **Próximo passo:** uma ação para hoje (ex.: conferir os números do `revisao-conferir.txt` e marcar a devolutiva com o cliente). A Fran apresenta o relatório em reunião, não só envia.

## Variante: auditoria (ISO 22000, FSSC, APPCC)
Use `"tipo": "auditoria"`. O relatório vira "Relatório de Auditoria", com a seção extra **Mapeamento de cláusulas (referência a conferir)**. Em `referencia` escreva o esquema e o tema da cláusula (ex.: "ISO 22000, controle operacional") e mantenha `a conferir` salvo leitura do texto oficial/vigente nesta conversa. Não afirme conformidade ou certificação; não prometa resultado em auditoria (§4).

## Schema do JSON
```json
{
  "cliente": "Padaria Pão Quente",
  "data": "29/10/2026",
  "consultora": "Nome da consultora",
  "contato": "Dona Maria",
  "tipo": "visita",
  "pontos_positivos": ["Equipe receptiva"],
  "itens": [
    {
      "area": "Câmara fria",
      "achado": "O que foi visto, uma vez só",
      "evidencia_foto": "caminho/da/foto.jpg",
      "risco": "alto",
      "referencia": "",
      "referencia_status": "a conferir",
      "acao": "Ação corretiva",
      "responsavel": "Pessoa",
      "prazo": "imediato",
      "impacto": "opcional: impacto financeiro para este cliente"
    }
  ],
  "observacoes": "texto livre"
}
```
- Obrigatórios: `cliente`, `data` (dd/mm/aaaa), e por item `risco` (`alto|medio|baixo`). `tipo`: `visita` (padrão) ou `auditoria`.
- `contato`, `pontos_positivos`, `impacto`, `observacoes`: opcionais. `evidencia_foto`: caminho absoluto ou relativo ao diretório de execução (foto ausente não quebra: aparece "foto não localizada").
- `prazo`: `imediato`, `N dias`, `N semanas`, `N meses` ou `dd/mm/aaaa`. Define a ordem do plano dentro de cada risco.
- Códigos NC01, NC02... seguem a ordem dos itens no JSON (a ordem da visita). O plano é reordenado por risco e prazo.
- Qualquer `referencia_status` diferente de `conferida` (ou `conferida` sem referência escrita) vale `a conferir`.

## Limites
- É rascunho: a consultora confere e assina. O risco é avaliação dela, o gerador só organiza.
- Fotos, nomes e dados do cliente ficam na máquina; não subir em serviço externo sem autorização.
- Exemplo completo: `exemplos/` (JSON, imagens ilustrativas, relatório gerado).
