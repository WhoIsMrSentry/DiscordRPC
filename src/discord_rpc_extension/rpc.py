from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
import time

from pypresence import Presence
from pypresence.exceptions import DiscordNotFound, PipeClosed, ResponseTimeout

from .config import AppConfig
from .spotify import build_spotify_client, get_now_playing_state

logger = logging.getLogger("discord_rpc_extension")


@dataclass(frozen=True)
class RpcRuntime:
    start_unix: int


def run_presence_loop(config: AppConfig) -> bool:
    runtime = RpcRuntime(start_unix=int(datetime.now().timestamp()))

    def connect(max_attempts: int = 10) -> Presence | None:
        """Try to connect to Discord RPC with retries.

        Returns a connected Presence or None if Discord isn't reachable.
        """

        backoff_seconds = 1

        pipes_to_try = (
            [config.discord_rpc_pipe]
            if config.discord_rpc_pipe is not None
            else list(range(0, 10))
        )

        for attempt in range(1, max_attempts + 1):
            pipe = pipes_to_try[(attempt - 1) % len(pipes_to_try)]
            client = Presence(
                config.discord_client_id,
                pipe=pipe,
                connection_timeout=config.discord_connection_timeout,
                response_timeout=config.discord_response_timeout,
            )
            try:
                logger.info(
                    "Discord RPC bağlanılıyor... (deneme %s/%s, pipe=%s)",
                    attempt,
                    max_attempts,
                    pipe,
                )
                client.connect()
                logger.info("Discord RPC bağlantısı kuruldu.")
                return client
            except DiscordNotFound:
                logger.error(
                    "Discord bulunamadı. Discord masaüstü uygulamasını açıp giriş yapın, sonra tekrar deneyin."
                )
                return None
            except (ResponseTimeout, PipeClosed):
                logger.warning(
                    "Discord RPC bağlantısı zaman aşımına uğradı. %ss sonra tekrar denenecek...",
                    backoff_seconds,
                )
                try:
                    client.close()
                except Exception:
                    pass
                time.sleep(backoff_seconds)
                backoff_seconds = min(backoff_seconds * 2, 30)

        logger.error("Discord RPC'ye bağlanılamadı (çok fazla deneme).")
        return None

    rpc = connect()
    if rpc is None:
        return False

    sp = build_spotify_client(config)

    last_spotify_fetch = 0.0
    cached_state = "Starting..."
    cached_large_text = "Spotify"

    party_size = 97
    party_max = 100

    try:
        while True:
            try:
                now = time.time()
                if now - last_spotify_fetch >= config.spotify_poll_seconds:
                    cached_state, cached_large_text = get_now_playing_state(sp)
                    last_spotify_fetch = now

                state, large_text = cached_state, cached_large_text

                payload: dict[str, object] = {
                    "details": "VSCode Module Write 87/100",
                    "state": state,
                    "start": runtime.start_unix,
                    "large_text": large_text,
                    "party_id": "party123",
                    "party_size": [party_size, party_max],
                }

                if config.discord_large_image:
                    payload["large_image"] = config.discord_large_image
                if config.discord_join_secret:
                    payload["join"] = config.discord_join_secret

                try:
                    rpc.update(**payload)
                    # Kullanıcıya görünür bir "heartbeat" log'u.
                    logger.info("RPC güncellendi: %s", state)
                except (ResponseTimeout, PipeClosed):
                    logger.warning(
                        "Discord RPC yanıt vermedi (timeout/pipe closed). Yeniden bağlanılıyor..."
                    )
                    try:
                        rpc.close()
                    except Exception:
                        pass
                    rpc = connect()
                    if rpc is None:
                        return False
                time.sleep(config.poll_seconds)

            except KeyboardInterrupt:
                logger.info("Kapatılıyor...")
                break
            except Exception:
                logger.exception("RPC güncelleme hatası")
                time.sleep(config.poll_seconds)

    finally:
        try:
            rpc.close()
        except Exception:
            pass

    return True
