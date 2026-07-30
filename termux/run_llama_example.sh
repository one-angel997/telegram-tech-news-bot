#!/data/data/com.termux/files/usr/bin/sh
# Esempio di invocazione di llama.cpp (modifica MODEL_PATH/LLAMA_CPP_PATH come necessario)
LLAMA_CPP_PATH="$HOME/llama.cpp/main"
MODEL_PATH="$HOME/models/tuo_modello.gguf"
PROMPT="Riassumi in italiano: Ciao mondo"
"$LLAMA_CPP_PATH" -m "$MODEL_PATH" -p "$PROMPT" --n_predict 128
