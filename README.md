## Installazione e uso di llama.cpp e modelli quantizzati su Termux

Questa sezione spiega come compilare llama.cpp su Termux, scaricare un modello ggml/gguf quantizzato e configurare il bot per usare il modello locale per i riassunti.

ATTENZIONE: il download di alcuni modelli può richiedere l'accesso a Hugging Face e l'accettazione di licenze. Verifica sempre i termini d'uso.

Requisiti minimi consigliati
- Android con Termux
- Almeno 4 GB di RAM (la procedura mira a usare modelli da ~2-3GB quantizzati)
- Spazio libero su disco: almeno 5 GB (dipende dal modello)

1) Compilare llama.cpp in Termux

Esegui i seguenti comandi in Termux:

```bash
pkg update && pkg upgrade -y
pkg install git clang make python wget -y

# Clona e compila llama.cpp
cd $HOME
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make

# L'eseguibile sarà in $HOME/llama.cpp/main
```

Se `make` fallisce per limiti di memoria, prova a compilare sul PC e trasferire l'eseguibile su Termux (cartella $HOME/llama.cpp/).

2) Scaricare un modello quantizzato (ggml/gguf)

Cerca modelli già convertiti in formato ggml/gguf e quantizzati (4-bit) su Hugging Face o TheBloke. Esempi di tag da cercare: "ggml", "gguf", "q4_0", "quantized".

Consigli pratici:
- Modelli ~3B quantizzati sono il compromesso per devices con 4GB RAM.
- Se trovi modelli alpaca/llama-derivates in formato ggml/gguf, preferiscili.

Salva il file modello nella cartella $HOME/models/ e imposta la variabile d'ambiente:

```bash
export MODEL_PATH="$HOME/models/tuo_modello.gguf"
```

3) (Opzionale) Creare uno swap file per evitare OOM

Se hai spazio libero su storage e vedi OOM, puoi creare uno swapfile (più lento, usalo solo se necessario):

```bash
fallocate -l 2G /sdcard/swapfile
mkswap /sdcard/swapfile
swapon /sdcard/swapfile
```

Nota: su alcuni dispositivi `fallocate` non è disponibile; usa `dd if=/dev/zero of=/sdcard/swapfile bs=1M count=2048`.

4) Configurare LLAMA_CPP_PATH e MODEL_PATH

Nel tuo ambiente Termux (o nello script widget), esporta le variabili:

```bash
export LLAMA_CPP_PATH="$HOME/llama.cpp/main"
export MODEL_PATH="$HOME/models/tuo_modello.gguf"
export TELEGRAM_BOT_TOKEN="1234567890:ABC..."
```

5) Esempi di script utili inclusi nel repo

- termux/install_llama.sh: script che automatizza il `git clone` e `make` di llama.cpp.
- termux/create_swap.sh: script per creare un swapfile (opzionale).
- termux/run_llama_example.sh: esempio di esecuzione di llama.cpp con prompt semplice.

Contenuto degli script (già presenti in repo):

termux/install_llama.sh
```bash
#!/data/data/com.termux/files/usr/bin/sh
set -e
pkg update -y
pkg install -y git clang make
cd "$HOME"
if [ ! -d "$HOME/llama.cpp" ]; then
  git clone https://github.com/ggerganov/llama.cpp.git
fi
cd llama.cpp
make
echo "Compilazione completata. Eseguibile: $HOME/llama.cpp/main"
```

termux/create_swap.sh
```bash
#!/data/data/com.termux/files/usr/bin/sh
# Crea uno swapfile da 2GB su /sdcard (se hai spazio). Modifica il percorso se serve.
SWAP_PATH="/sdcard/swapfile"
if [ -f "$SWAP_PATH" ]; then
  echo "Swapfile già presente: $SWAP_PATH"
  exit 0
fi
# Usa dd se fallisce fallocate
if command -v fallocate >/dev/null 2>&1; then
  fallocate -l 2G "$SWAP_PATH"
else
  dd if=/dev/zero of="$SWAP_PATH" bs=1M count=2048
fi
mkswap "$SWAP_PATH"
swapon "$SWAP_PATH"
echo "Swap attivato: $SWAP_PATH"
```

termux/run_llama_example.sh
```bash
#!/data/data/com.termux/files/usr/bin/sh
# Esempio di invocazione di llama.cpp (modifica MODEL_PATH/LLAMA_CPP_PATH come necessario)
LLAMA_CPP_PATH="$HOME/llama.cpp/main"
MODEL_PATH="$HOME/models/tuo_modello.gguf"
PROMPT="Riassumi in italiano: Ciao mondo"
"$LLAMA_CPP_PATH" -m "$MODEL_PATH" -p "$PROMPT" --n_predict 128
```

6) Integrazione con il bot

Il bot (bot.py) chiama l'eseguibile definito in LLAMA_CPP_PATH con il modello definito in MODEL_PATH. Assicurati di esportare queste variabili prima di lanciare `python3 bot.py` o di inserirle nello script Termux:Widget.

7) Risorse e link utili

- llama.cpp: https://github.com/ggerganov/llama.cpp
- TheBloke (modelli convertiti): https://huggingface.co/TheBloke
- Hugging Face: https://huggingface.co


Se vuoi, posso suggerire uno specifico file modello da scaricare (se mi dici se preferisci Alpaca-like, Vicuna‑derived, ecc.) e preparare il comando `wget` diretto se il modello è pubblicamente disponibile senza autenticazione. Altrimenti, la guida sopra copre i passaggi necessari per compilare e configurare l'ambiente su Termux.
