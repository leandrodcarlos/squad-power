#!/usr/bin/env bash
# Instalador do Squad Power (Mac e Linux). Opções: --sem-plugins --sem-python
set -u
RAIZ="$(cd "$(dirname "$0")" && pwd)"
DESTINO="${CLAUDE_DESTINO:-$HOME/.claude}"
SEM_PLUGINS=0
SEM_PYTHON=0
for arg in "$@"; do
  case "$arg" in
    --sem-plugins) SEM_PLUGINS=1 ;;
    --sem-python) SEM_PYTHON=1 ;;
    *) echo "Opção desconhecida: $arg" >&2; exit 2 ;;
  esac
done
AVISOS=()

# Troca {{SQUAD_ROOT}} sem sed: o caminho pode ter espaço, & ou /.
copiar() {
  RAIZ_AWK="$RAIZ" awk 'BEGIN { m = "{{SQUAD_ROOT}}"; r = ENVIRON["RAIZ_AWK"] }
    { s = ""; l = $0
      while ((i = index(l, m)) > 0) { s = s substr(l, 1, i - 1) r; l = substr(l, i + length(m)) }
      print s l }' "$1" > "$2"
}

mkdir -p "$DESTINO/agents"
n_ag=0
n_sk=0
for f in "$RAIZ"/agents/*-fran.md; do
  [ -e "$f" ] || { echo "Nenhum agente em $RAIZ/agents" >&2; exit 1; }
  copiar "$f" "$DESTINO/agents/$(basename "$f")"
  n_ag=$((n_ag + 1))
done
for d in "$RAIZ"/skills/*/; do
  [ -f "$d/SKILL.md" ] || continue
  nome="$(basename "$d")"
  mkdir -p "$DESTINO/skills/$nome"
  copiar "$d/SKILL.md" "$DESTINO/skills/$nome/SKILL.md"
  n_sk=$((n_sk + 1))
done
echo "OK  $n_ag agentes e $n_sk skills instalados em $DESTINO (base em $RAIZ)"

if [ "$SEM_PYTHON" -eq 0 ]; then
  if command -v python3 >/dev/null 2>&1; then
    if python3 -m pip install --quiet --disable-pip-version-check --user -r "$RAIZ/requirements.txt" >/dev/null 2>&1; then
      echo "OK  bibliotecas Python instaladas"
    else
      AVISOS+=("Bibliotecas Python não instalaram. Rode: python3 -m pip install --user -r requirements.txt")
    fi
  else
    AVISOS+=("Python 3 não encontrado. No Mac: brew install python@3.11")
  fi
  command -v ffmpeg >/dev/null 2>&1 || AVISOS+=("ffmpeg não encontrado (só faz falta para transcrever áudio). No Mac: brew install ffmpeg")
fi

instalar_plugin() {
  claude plugin marketplace add "$1" >/dev/null 2>&1
  claude plugin install "$2" -y >/dev/null 2>&1
  claude plugin enable "$2" >/dev/null 2>&1
  if claude plugin list 2>/dev/null | grep -A4 -F "$2" | grep -q enabled; then
    echo "OK  plugin $2 ($3)"
  else
    AVISOS+=("Plugin $2 não ficou ativo. Rode: claude plugin install $2")
  fi
}

# Versões fixas: plugin roda com a permissão da usuária e não deve mudar sozinho.
if [ "$SEM_PLUGINS" -eq 0 ]; then
  if command -v claude >/dev/null 2>&1; then
    instalar_plugin "https://github.com/thedotmack/claude-mem.git#v10.6.2" claude-mem@thedotmack "memória entre conversas"
    instalar_plugin "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git#v2.15.0" ui-ux-pro-max@ui-ux-pro-max-skill "design de sites e propostas"
    instalar_plugin "https://github.com/anthropics/skills.git" document-skills@anthropic-agent-skills "Word, PowerPoint, Excel e PDF"
  else
    AVISOS+=("Comando claude não encontrado: instale o Claude Code e rode este instalador de novo.")
  fi
fi

if [ "${#AVISOS[@]}" -gt 0 ]; then
  echo
  echo "O squad funciona, mas falta resolver:"
  for m in "${AVISOS[@]}"; do echo "  - $m"; done
fi
echo
echo "Pronto. Feche e abra o Claude Code, depois digite: /squad-power"
