# Discord RPC extension

This repo updates Discord Rich Presence and shows the currently playing Spotify track in the `state` field.

## Setup

1) Virtual environment (optional but recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Dependencies

```powershell
pip install -r requirements.txt
```

Optional (editable install for the package/CLI):

```powershell
pip install -e .
```

3) Environment variables

- Copy `.env.example` to `.env` and fill in the values.
- `DISCORD_LARGE_IMAGE` is typically a Discord Developer Portal asset key. (Small image is currently not used.)

Spotify note: `SPOTIPY_REDIRECT_URI` must match **exactly** one of the values in Spotify Dashboard → “Redirect URIs” (including trailing `/` if present).

## Run

Recommended:

```powershell
python -m discord_rpc_extension
```

Alternative (backwards-compatible wrapper):

```powershell
python .\NewRPC\Rich_Presence.py
```

On first run, Spotify OAuth may open a browser window and create a token cache.
