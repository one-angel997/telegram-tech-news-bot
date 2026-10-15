#!/data/data/com.termux/files/usr/bin/sh
set -e

pkg install -y git cmake clang make

if [ ! -d "$HOME/llama.cpp/.git" ]; then
  git clone https://github.com/ggml-org/llama.cpp.git "$HOME/llama.cpp"
fi

cd "$HOME/llama.cpp"
cmake -S . -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_OPENMP=OFF \
  -DLLAMA_BUILD_SERVER=ON
cmake --build build --target llama-server --parallel 1

echo "Compilazione completata: $HOME/llama.cpp/build/bin/llama-server"
