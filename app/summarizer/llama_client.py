import json
import urllib.error
import urllib.request

from app.common.config import get_config


def summarize_text(text: str, target_chars: int = 600) -> str:
    config = get_config()
    llama_cfg = config.get("llama", {})
    base_url = (llama_cfg.get("server_url") or "http://127.0.0.1:8080").rstrip("/")
    timeout = int(llama_cfg.get("request_timeout") or 180)

    payload = json.dumps({
        "messages": [
            {
                "role": "system",
                "content": (
                    "Sei un assistente che riassume notizie in italiano. "
                    "Non inventare fatti. Rispetta sempre il contenuto della fonte."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Riassumi in italiano in massimo {target_chars} caratteri:\n\n"
                    f"{text[:6000]}"
                ),
            },
        ],
        "temperature": 0.2,
        "max_tokens": 256,
        "stream": False,
    }).encode("utf-8")

    request = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Errore durante il riassunto: {exc}") from exc

    try:
        content = result["choices"][0]["message"]["content"]
        return content.strip()
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Risposta del server LLM non valida")
