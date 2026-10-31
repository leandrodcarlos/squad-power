# Squad Power

Time de agentes de IA que aplica o método da Fran D'Carlos no dia a dia da consultora de alimentos: relatório de visita, proposta, BPF, norma, site, prospecção e gestão.

Tudo o que o squad entrega é rascunho. Você confere antes de mandar ao cliente.

## Instalar

Você precisa do [Claude Code](https://claude.com/claude-code) e de um plano Claude ativo.

**Windows.** Abra o PowerShell dentro desta pasta e rode:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

**Mac.** Abra o Terminal dentro desta pasta e rode:

```bash
bash install.sh
```

O instalador coloca agentes e skills no Claude Code, instala as bibliotecas Python e os plugins abaixo, e avisa no fim se faltou algo. Falta de Python ou ffmpeg não impede o squad de funcionar: só desliga a geração de `.docx` ou a transcrição de áudio.

Não mova nem apague esta pasta depois de instalar: os agentes leem a base daqui. Se mudar de lugar, rode o instalador de novo.

## Usar

Feche e abra o Claude Code. Abra-o na pasta onde quer salvar as entregas e digite:

```
/squad-power
```

Aparece o menu. Você também pode ir direto: `/squad-power *visita <suas anotações>`.

| Comando | Para quê | Entrega |
|---|---|---|
| `*visita` | anotações, áudio ou fotos da visita | relatório `.docx` e mensagem de WhatsApp |
| `*proposta` | orçar um serviço | proposta e roteiro da reunião |
| `*bpf` | Manual de BPF, POP, checklist | documento `.docx` |
| `*norma` | "é permitido?", rotulagem, vigência | norma, artigo e link oficial |
| `*site` | site de uma página, proposta caprichada | `.html`, `.docx`, `.pptx` ou `.pdf` |
| `*prospectar` | conseguir clientes | plano semanal e scripts |
| `*comecar` | nicho e plano de 90 dias | plano |
| `*padronizar` | tarefa que você repete | projeto para Claude, Gemini ou ChatGPT |
| `*revisar` | conferir antes de enviar | lista de ajustes |

## Os agentes

Para chamar um direto: "use a val-fran: quanto cobro por um manual de BPF?".

| Agente | Quando usar |
|---|---|
| `orquestradora-fran` | dúvida geral, "o que a Fran faria" |
| `aurora-fran` | nicho, missão, identidade |
| `helena-fran` | metas, plano, SWOT, 5W2H, indicadores |
| `val-fran` | preço, hora técnica, pacote, proposta |
| `isa-fran` | conteúdo, Instagram, LinkedIn |
| `camila-fran` | prospecção, reunião, objeções, follow-up |
| `sofia-fran` | caixa, processos, contratação, contrato |
| `bpf-fran` (Bia) | Manual de BPF, POP, checklist, ficha técnica |
| `visita-fran` (Vera) | visita, auditoria e plano de ação |
| `regulatorio-fran` (Rê) | norma ao vivo nas fontes oficiais, com link |
| `design-fran` (Dani) | site, proposta visual, apresentação |
| `revisora-fran` (Rita) | revisão final antes de enviar |

## Plugins instalados junto

| Plugin | O que faz | Origem |
|---|---|---|
| claude-mem | lembra o contexto entre conversas, salvo no seu computador | github.com/thedotmack/claude-mem |
| ui-ux-pro-max | estilos, paletas e fontes para sites | github.com/nextlevelbuilder/ui-ux-pro-max-skill |
| document-skills | Word, PowerPoint, Excel e PDF | github.com/anthropics/skills |

Para instalar só o squad: `install.ps1 -SemPlugins` no Windows ou `install.sh --sem-plugins` no Mac.

## Sem Claude Code

`skills/projeto-ia-fran/exemplos/` tem três kits prontos para Claude Projects, Gemini Gems e GPTs: relatório de visita, proposta comercial e POP. Cada pasta tem um `COMO-USAR.md`.

## Regras do squad

- **Rascunho:** confira toda entrega.
- **Norma:** sempre com link oficial, conferindo a vigência. Só o `regulatorio-fran` cita número de norma.
- **Fiscalização:** nenhum agente promete aprovação.
- **Dados de cliente:** não digite CPF, CNPJ ou dado sensível. O que entra na conversa vai para o serviço de IA e pode entrar na memória local.
- **Conteúdo:** material exclusivo da comunidade. Não repasse.

## Problemas comuns

| Sintoma | O que fazer |
|---|---|
| `/squad-power` não aparece | feche e abra o Claude Code; rode o instalador de novo |
| `.docx` não sai | rode `python -m pip install -r requirements.txt` |
| áudio não transcreve | instale o ffmpeg (o instalador mostra o comando) |
| PowerShell bloqueia o script | use o comando com `-ExecutionPolicy Bypass` acima |
| agente não acha a base | a pasta mudou de lugar: rode o instalador de novo |
