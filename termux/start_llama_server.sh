#!/data/data/com.termux/files/usr/bin/sh
set -eu

LLAMA_SERVER_PATH="${LLAMA_SERVER_PATH:-$HOME/llama.cpp/build/bin/llama-server}"
MODEL_PATH="${MODEL_PATH:-$HOME/models/Qwen3.5-0.8B-Q4_0.gguf}"
LLAMA_CONTEXT_SIZE="${LLAMA_CONTEXT_SIZE:-4096}"
LLAMA_THREADS="${LLAMA_THREADS:-4}"

if [ ! -x "$LLAMA_SERVER_PATH" ]; then
  echo "llama-server non trovato o non eseguibile: $LLAMA_SERVER_PATH" >&2
  echo "Esegui prima termux/install_llama.sh oppure imposta LLAMA_SERVER_PATH." >&2
  exit 1
fi

if [ ! -f "$MODEL_PATH" ]; then
  echo "Modello GGUF non trovato: $MODEL_PATH" >&2
  echo "Scarica il modello oppure imposta MODEL_PATH." >&2
  exit 1
fi

exec "$LLAMA_SERVER_PATH" \
  --model "$MODEL_PATH" \
  --ctx-size "$LLAMA_CONTEXT_SIZE" \
  --threads "$LLAMA_THREADS" \
  --host 127.0.0.1 \
  --port 8080
