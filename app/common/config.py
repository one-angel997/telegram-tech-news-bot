import os
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
PROFILE = os.getenv("BOT_PROFILE", "tech_news")
ENV_PATH = ROOT / "bots" / PROFILE / ".env"
CONFIG_PATH = ROOT / "bots" / PROFILE / "config.yaml"


def _resolve_env_value(value):
    if not isinstance(value, str):
        return value
    if value.startswith("${") and value.endswith("}"):
        env_name = value[2:-1]
        return os.getenv(env_name, "")
    return value


def load_env():
    if not ENV_PATH.exists():
        return

    with ENV_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def load_config():
    load_env()

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG_PATH}")

    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    if isinstance(raw, dict):
        bot_cfg = raw.get("bot", {})
        if isinstance(bot_cfg, dict) and "token" in bot_cfg:
            bot_cfg["token"] = _resolve_env_value(bot_cfg.get("token", ""))

    return raw


def get_config():
    return load_config()
