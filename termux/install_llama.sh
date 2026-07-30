#!/data/data/com.termux/files/usr/bin/sh
# Script per clonare e compilare llama.cpp su Termux
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
