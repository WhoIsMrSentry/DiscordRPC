from __future__ import annotations

from dataclasses import dataclass
import os


def _first_non_empty(*values: str | None) -> str | None:
    for value in values:
        if value is not None and str(value).strip() != "":
            return str(value)
    return None


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Eksik ortam değişkeni: {name}. '.env.example' dosyasına bakıp '.env' oluşturun."
        )
    return value


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = str(value).strip()
    if trimmed == "":
        return None
    lowered = trimmed.lower()
    if lowered in {"none", "null", "()"}:
        return None
    # Bazı eski ayarlarda "0" kullanılmış; Discord asset key olarak anlamlı değilse boş say.
    if trimmed == "0":
        return None
    return trimmed


@dataclass(frozen=True)
class AppConfig:
    discord_client_id: str

    # Discord RPC large/small image alanları bazı kurulumlarda asset key, bazı kurulumlarda URL ile de çalışabiliyor.
    # Bu yüzden tek alanı esnek tutuyoruz.
    discord_large_image: str | None
    discord_join_secret: str | None

    discord_rpc_pipe: int | None
    discord_connection_timeout: int
    discord_response_timeout: int

    spotify_client_id: str
    spotify_client_secret: str
    spotify_redirect_uri: str

    spotify_poll_seconds: int

    poll_seconds: int


def load_config() -> AppConfig:
    # python-dotenv ile .env yükleme (opsiyonel)
    try:
        from dotenv import load_dotenv

        # override=True: Windows ortam değişkeni daha önce set edildiyse bile .env ile ez.
        load_dotenv(override=True)
    except Exception:
        pass

    discord_client_id = _require("DISCORD_CLIENT_ID")

    # Geriye dönük uyumluluk: eski KEY isimleri
    discord_large_image = _normalize_optional(
        _first_non_empty(
        os.getenv("DISCORD_LARGE_IMAGE"),
        os.getenv("DISCORD_LARGE_IMAGE_KEY"),
        )
    )

    discord_join_secret = os.getenv("DISCORD_JOIN_SECRET")

    discord_pipe_raw = os.getenv("DISCORD_RPC_PIPE")
    try:
        discord_rpc_pipe = int(discord_pipe_raw) if discord_pipe_raw else None
    except ValueError:
        discord_rpc_pipe = None

    conn_timeout_raw = os.getenv("DISCORD_CONNECTION_TIMEOUT", "30")
    resp_timeout_raw = os.getenv("DISCORD_RESPONSE_TIMEOUT", "30")
    try:
        discord_connection_timeout = max(5, int(conn_timeout_raw))
    except ValueError:
        discord_connection_timeout = 30
    try:
        discord_response_timeout = max(5, int(resp_timeout_raw))
    except ValueError:
        discord_response_timeout = 30

    spotify_client_id = _require("SPOTIPY_CLIENT_ID")
    spotify_client_secret = _require("SPOTIPY_CLIENT_SECRET")
    spotify_redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8080")

    spotify_poll_raw = os.getenv("SPOTIFY_POLL_SECONDS", "30")
    try:
        spotify_poll_seconds = max(10, int(spotify_poll_raw))
    except ValueError:
        spotify_poll_seconds = 30

    poll_seconds_raw = os.getenv("POLL_SECONDS", "15")
    try:
        poll_seconds = max(5, int(poll_seconds_raw))
    except ValueError:
        poll_seconds = 15

    return AppConfig(
        discord_client_id=discord_client_id,
        discord_large_image=discord_large_image,
        discord_join_secret=discord_join_secret,
        discord_rpc_pipe=discord_rpc_pipe,
        discord_connection_timeout=discord_connection_timeout,
        discord_response_timeout=discord_response_timeout,
        spotify_client_id=spotify_client_id,
        spotify_client_secret=spotify_client_secret,
        spotify_redirect_uri=spotify_redirect_uri,
        spotify_poll_seconds=spotify_poll_seconds,
        poll_seconds=poll_seconds,
    )
