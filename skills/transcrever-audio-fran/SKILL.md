---
name: transcrever-audio-fran
description: Transcreve áudio ou vídeo de visita técnica (gravado no celular) em texto limpo PT-BR, direto no computador, sem enviar nada para a internet. Use quando a consultora pedir "transcrever áudio", "áudio da visita", "transcreve esse áudio", "áudio do WhatsApp", "transcrição de reunião" ou soltar um arquivo .m4a, .ogg, .opus, .mp3, .wav ou .mp4. Usa GPU quando existe e cai para CPU sozinho. A transcrição alimenta a skill relatorio-visita-fran.
---

# Transcrever áudio da visita

## Quando usar
A consultora gravou anotações da visita (ou uma reunião) e quer o texto. Aceita `.m4a`, `.ogg`, `.opus` (WhatsApp), `.mp3`, `.wav`, `.mp4` e outros formatos que o ffmpeg abre.

## Comando
```
python "{{SQUAD_ROOT}}/skills/transcrever-audio-fran/transcrever.py" "<arquivo>" ["<arquivo2>" ...] [--modelo medium] [--saida PASTA] [--timestamps]
```
- `--timestamps`: põe `[mm:ss]` no início de cada trecho (útil para voltar ao áudio).
- `--modelo`: padrão `medium` na GPU e `small` na CPU. Use `large-v3` só em GPU boa.
- Vários arquivos de uma vez: ele transcreve em fila.

## Onde sai
`<nome do arquivo> - Transcrição.txt` ao lado do áudio (ou na pasta de `--saida`). Se a execução cair no meio, rode o mesmo comando de novo: ele retoma da última parte de 20 minutos concluída.

## Antes de rodar
1. Precisa de Python 3.10+ e do `ffmpeg` (Windows: `winget install Gyan.FFmpeg`). Sem ele o script avisa em português.
2. Precisa do pacote: `pip install faster-whisper`. Para GPU NVIDIA: `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12`. Sem GPU, funciona em CPU, só mais devagar (áudio de 10 min leva alguns minutos).
3. Na primeira vez o modelo é baixado uma vez (internet só nesse momento; depois roda offline).

## Privacidade
O áudio nunca sai da máquina: a transcrição é feita localmente. Não suba o áudio nem o texto em serviço externo sem autorização do cliente visitado.

## Limites (sempre avisar a consultora)
- O Whisper pode errar termo técnico, nome próprio, marca e **número de norma** (RDC 216, RDC 275, Portaria 2619...). Toda transcrição vai para **revisão humana**; nunca citar número de norma sem conferir na fonte.
- Um pós-ajuste conservador corrige só siglas: RDC, ANVISA, BPF, APPCC, POP/POPs.
- Áudio com ruído de cozinha, vento ou várias pessoas falando junto piora o resultado. Grave perto da boca.
- Trechos de silêncio são cortados (VAD). Fala muito baixa pode sumir.

## Próximo passo
Para relatório de visita use **relatorio-visita-fran**: entregue a ele o `.txt` revisado.
