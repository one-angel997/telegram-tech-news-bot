#!/data/data/com.termux/files/usr/bin/sh
set -eu

# Avvia in un unico comando llama-server, Tech News Bot e F1 News Bot.
# Aggiungi Termux alle eccezioni delle ottimizzazioni batteria e usa
# `termux-wake-lock` per ridurre il rischio che Android sospenda i processi.

cd "$HOME/telegram-tech-news-bot" || {
  echo "Repository non trovato in $HOME/telegram-tech-news-bot" >&2
  exit 1
}

PYTHON="$PWD/.venv/bin/python"
STATE_DIR="$HOME/.local/state/telegram-news-bot"
mkdir -p "$STATE_DIR"

if [ ! -x "$PYTHON" ]; then
  echo "Python dell'ambiente virtuale non trovato: $PYTHON" >&2
  echo "Crea prima .venv e installa requirements.txt." >&2
  exit 1
fi

if [ ! -f "bots/tech_news/.env" ] || [ ! -f "bots/f1_news/.env" ]; then
  echo "Crea prima bots/tech_news/.env e bots/f1_news/.env con i rispettivi token." >&2
  exit 1
fi

start_process() {
  name="$1"
  shift

  pid_file="$STATE_DIR/$name.pid"
  log_file="$STATE_DIR/$name.log"

  if [ -f "$pid_file" ]; then
    old_pid=$(cat "$pid_file" 2>/dev/null || true)
    if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
      echo "$name risulta già avviato (PID $old_pid)."
      return
    fi
  fi

  rm -f "$pid_file"
  nohup "$@" >> "$log_file" 2>&1 </dev/null &
  echo "$!" > "$pid_file"
  echo "Avviato $name (PID $(cat "$pid_file"))."
  echo "Log: $log_file"
}

# Usa llama-server già attivo, se presente.
if ! curl -fsS http://127.0.0.1:8080/health >/dev/null 2>&1; then
  start_process llama-server sh termux/start_llama_server.sh

  echo "Attendo che llama-server sia pronto..."
  ready=0
  attempt=0

  while [ "$attempt" -lt 120 ]; do
    if curl -fsS http://127.0.0.1:8080/health >/dev/null 2>&1; then
      ready=1
      break
    fi

    attempt=$((attempt + 1))
    sleep 2
  done

  if [ "$ready" -ne 1 ]; then
    echo "llama-server non ha risposto entro il tempo previsto." >&2
    echo "Controlla $STATE_DIR/llama-server.log" >&2
    exit 1
  fi
else
  echo "llama-server è già attivo su 127.0.0.1:8080."
fi

# Gli entrypoint selezionano autonomamente il rispettivo profilo.
unset BOT_PROFILE
start_process tech-news "$PYTHON" run_tech_news.py
start_process f1-news "$PYTHON" run_f1_news.py

echo "Avvio completato."
