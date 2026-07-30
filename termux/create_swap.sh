#!/data/data/com.termux/files/usr/bin/sh
# Script per creare swap su /sdcard (2GB). Usalo con cautela.
SWAP_PATH="/sdcard/swapfile"
if [ -f "$SWAP_PATH" ]; then
  echo "Swapfile già presente: $SWAP_PATH"
  exit 0
fi
if command -v fallocate >/dev/null 2>&1; then
  fallocate -l 2G "$SWAP_PATH"
else
  dd if=/dev/zero of="$SWAP_PATH" bs=1M count=2048
fi
mkswap "$SWAP_PATH"
swapon "$SWAP_PATH"
echo "Swap attivato: $SWAP_PATH"
