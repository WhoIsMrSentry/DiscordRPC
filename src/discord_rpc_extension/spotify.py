from __future__ import annotations

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .config import AppConfig


def build_spotify_client(config: AppConfig) -> spotipy.Spotify:
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=config.spotify_client_id,
            client_secret=config.spotify_client_secret,
            redirect_uri=config.spotify_redirect_uri,
            scope="user-read-currently-playing",
        )
    )


def get_now_playing_state(sp: spotipy.Spotify) -> tuple[str, str]:
    """Returns (state, large_text)."""

    current = sp.currently_playing()
    if current and current.get("item"):
        item = current["item"]
        song_name = item.get("name") or "Unknown"
        artists = item.get("artists") or []
        artist_name = (artists[0].get("name") if artists else None) or "Unknown"
        state = f"Listening: {song_name} — {artist_name}"
        large_text = "Spotify"
        return state, large_text

    return "Spotify: Not playing", "Spotify"
