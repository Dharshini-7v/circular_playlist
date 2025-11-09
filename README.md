# Circular Music Playlist (FastAPI + HTML/JS)

A small web app demonstrating classic data structures:
- Circular Doubly Linked List for the playlist
- Stack for history
- Queue for up next

Includes a FastAPI backend and a static HTML/JS frontend served by the backend.

## Features
- Add/remove songs
- Next/previous navigation (circular)
- Up Next queue and History stack
- Two implementations: Circular (linked list) and List
- Seed 4 popular tracks with 30s preview audio (iTunes API)
- Favorites and simple login (in-memory)
- Login-first UI with optional "Remember me"

## Project structure
- `playlist_app/` core models and data structures
- `playlist_api/server.py` FastAPI app and routes
- `web/` frontend (index.html, app.js, styles.css)
- `requirements.txt` dependencies

## Run locally (Windows)
1. Python 3.11+ recommended
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Start backend (serves frontend at /web):
   ```bash
   python -m uvicorn playlist_api.server:app --reload --host 127.0.0.1 --port 9000
   ```
4. Open the app:
   - http://127.0.0.1:9000/

## API quick reference
- `GET /health`
- `GET /songs`, `POST /songs`, `DELETE /songs/{id}`
- `GET /play`, `POST /next`, `POST /previous`
- `POST /enqueue`, `GET /queue`, `GET /history`
- `POST /impl` (circular | list)
- `POST /seed` (adds 4 tracks with preview URLs)
- `GET /me`, `POST /login`, `POST /logout`
- `GET /favorites`, `POST /favorites`, `DELETE /favorites/{song_id}`

## Deploy options
- Single-app hosting (preferred): Render/Railway/Fly.io using Uvicorn
  - Start command: `python -m uvicorn playlist_api.server:app --host 0.0.0.0 --port $PORT`
- Split hosting:
  - Frontend on GitHub Pages, backend on Render
  - If splitting, change `web/app.js` `API` to your backend URL

## GitHub
Initialize and push (replace YOUR_USERNAME/playlist-app):
```bash
git init
git branch -M main
git add .
git commit -m "Initial commit: FastAPI + web UI playlist"
git remote add origin https://github.com/YOUR_USERNAME/playlist-app.git
git push -u origin main
```

## Notes
- In-memory data (no DB). If you want persistence (JSON/SQLite), open an issue or contribute.
- Make sure to allow Uvicorn in your firewall on first run.
