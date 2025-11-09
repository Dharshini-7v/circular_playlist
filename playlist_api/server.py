from __future__ import annotations

# Demo MP3 fallback URLs (royalty-free for testing)
DEMO_URLS: dict[str, str] = {
    # Popular song names mapped to demo audio (compat)
    "Blinding Lights": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "Shape of You": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "Levitating": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "Someone Like You": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    # SoundHelix exact titles for better UX alignment
    "SoundHelix Song 1": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "SoundHelix Song 2": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "SoundHelix Song 3": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "SoundHelix Song 4": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
}

def _demo_url_for(title: str) -> str | None:
    key = (title or "").strip()
    return DEMO_URLS.get(key)
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, Response
from pathlib import Path
from urllib import parse, request
import json

from playlist_app.playlist import CircularPlaylist, ListPlaylist


class SongIn(BaseModel):
    title: str
    artist: str
    duration_sec: int | None = 0
    audio_url: str | None = None


class EnqueueIn(BaseModel):
    song_id: int


class ImplIn(BaseModel):
    impl: Literal["circular", "list"]


class LoginIn(BaseModel):
    username: str


app = FastAPI(title="Circular Music Playlist API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Determine path to web folder and mount static files
web_dir = (Path(__file__).resolve().parents[1] / "web")
if web_dir.exists():
    app.mount("/web", StaticFiles(directory=str(web_dir), html=True), name="web")

# Redirect root to /web/ for convenience
@app.get("/")
def root():
    return RedirectResponse(url="/web/", status_code=307)

# Avoid 404 noise for favicon
@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


# simple in-memory state
_state = {
    "impl": "circular",
    "circular": CircularPlaylist(),
    "list": ListPlaylist(),
    "user": None,  # simple in-memory username
    "favorites": set(),  # song id set
}


def _active():
    return _state[_state["impl"]]


@app.get("/health")
def health():
    return {"status": "ok"}


def fetch_itunes_preview(title: str, artist: str) -> str | None:
    try:
        term = f"{title} {artist}"
        qs = parse.urlencode({"term": term, "entity": "song", "limit": 1})
        url = f"https://itunes.apple.com/search?{qs}"
        with request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        results = data.get("results") or []
        if results:
            return results[0].get("previewUrl")
    except Exception:
        pass
    return None


@app.get("/songs")
def list_songs():
    songs = _active().list_songs()
    return [
        {"id": s.id, "title": s.title, "artist": s.artist, "duration_sec": s.duration_sec, "audio_url": s.audio_url}
        for s in songs
    ]


@app.post("/songs", status_code=201)
def add_song(song: SongIn):
    audio_url = song.audio_url
    if not audio_url:
        audio_url = fetch_itunes_preview(song.title, song.artist) or _demo_url_for(song.title)
    s = _active().add_song(song.title, song.artist, song.duration_sec or 0, audio_url)
    return {"id": s.id, "title": s.title, "artist": s.artist, "duration_sec": s.duration_sec, "audio_url": s.audio_url}


@app.delete("/songs/{song_id}")
def delete_song(song_id: int):
    ok = _active().remove_song(song_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Song not found")
    return {"removed": True}


@app.get("/play")
def play():
    s = _active().play()
    if not s:
        return {"song": None}
    if s and not s.audio_url:
        preview = fetch_itunes_preview(s.title, s.artist)
        s.audio_url = preview or _demo_url_for(s.title)
    return {"song": {"id": s.id, "title": s.title, "artist": s.artist, "duration_sec": s.duration_sec, "audio_url": s.audio_url}}


@app.post("/next")
def next_song():
    s = _active().next()
    if s and not s.audio_url:
        preview = fetch_itunes_preview(s.title, s.artist)
        s.audio_url = preview or _demo_url_for(s.title)
    return {"song": (None if not s else {"id": s.id, "title": s.title, "artist": s.artist, "duration_sec": s.duration_sec, "audio_url": s.audio_url})}


@app.post("/previous")
def previous_song():
    s = _active().previous()
    if s and not s.audio_url:
        preview = fetch_itunes_preview(s.title, s.artist)
        s.audio_url = preview or _demo_url_for(s.title)
    return {"song": (None if not s else {"id": s.id, "title": s.title, "artist": s.artist, "duration_sec": s.duration_sec, "audio_url": s.audio_url})}


@app.post("/enqueue")
def enqueue(in_data: EnqueueIn):
    ok = _active().enqueue_next(in_data.song_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Song not found to enqueue")
    return {"enqueued": True}


@app.get("/queue")
def get_queue():
    q = list(_active().up_next)
    return [
        {"id": s.id, "title": s.title, "artist": s.artist, "duration_sec": s.duration_sec, "audio_url": s.audio_url}
        for s in q
    ]


@app.get("/history")
def get_history():
    h = list(_active().history)
    return [
        {"id": s.id, "title": s.title, "artist": s.artist, "duration_sec": s.duration_sec, "audio_url": s.audio_url}
        for s in h
    ]


@app.post("/impl")
def switch_impl(body: ImplIn):
    _state["impl"] = body.impl
    return {"impl": _state["impl"]}


@app.post("/seed")
def seed():
    samples = [
        ("Blinding Lights", "The Weeknd", 200),
        ("Shape of You", "Ed Sheeran", 233),
        ("Levitating", "Dua Lipa", 203),
        ("Someone Like You", "Adele", 285),
    ]
    added = []
    for t, a, d in samples:
        preview = fetch_itunes_preview(t, a) or _demo_url_for(t)
        s = _active().add_song(t, a, d, preview)
        added.append({"id": s.id, "title": s.title, "artist": s.artist, "duration_sec": s.duration_sec, "audio_url": s.audio_url})
    return {"seeded": len(added), "songs": added}


@app.post("/seed_fast")
def seed_fast():
    # Use titles that match the demo audio so names and sound align
    samples = [
        ("SoundHelix Song 1", "SoundHelix", 200),
        ("SoundHelix Song 2", "SoundHelix", 233),
        ("SoundHelix Song 3", "SoundHelix", 203),
        ("SoundHelix Song 4", "SoundHelix", 285),
    ]
    added = []
    for t, a, d in samples:
        s = _active().add_song(t, a, d, _demo_url_for(t))
        added.append({"id": s.id, "title": s.title, "artist": s.artist, "duration_sec": s.duration_sec, "audio_url": s.audio_url})
    return {"seeded": len(added), "songs": added}


# Auto-seed on startup quickly (no preview lookups)
@app.on_event("startup")
def _auto_seed_on_startup():
    try:
        if not _active().list_songs():
            for t, a, d in [
                ("SoundHelix Song 1", "SoundHelix", 200),
                ("SoundHelix Song 2", "SoundHelix", 233),
                ("SoundHelix Song 3", "SoundHelix", 203),
                ("SoundHelix Song 4", "SoundHelix", 285),
            ]:
                _active().add_song(t, a, d, _demo_url_for(t))
    except Exception:
        pass


# --- Simple auth and favorites ---
@app.get("/me")
def me():
    return {"user": _state["user"]}


@app.post("/login")
def login(body: LoginIn):
    _state["user"] = body.username.strip() or None
    return {"user": _state["user"]}


@app.post("/logout")
def logout():
    _state["user"] = None
    _state["favorites"] = set()
    return {"ok": True}


@app.get("/favorites")
def get_favorites():
    ids = list(_state["favorites"]) if _state["favorites"] else []
    all_songs = {s.id: s for s in _active().list_songs()}
    out = []
    for sid in ids:
        s = all_songs.get(sid)
        if s:
            out.append({"id": s.id, "title": s.title, "artist": s.artist, "duration_sec": s.duration_sec, "audio_url": s.audio_url})
    return out


@app.post("/favorites")
def add_favorite(in_data: EnqueueIn):
    # reuse EnqueueIn for song_id
    # validate song exists
    songs = _active().list_songs()
    if not any(s.id == in_data.song_id for s in songs):
        raise HTTPException(status_code=404, detail="Song not found")
    _state["favorites"].add(in_data.song_id)
    return {"favorited": True}


@app.delete("/favorites/{song_id}")
def remove_favorite(song_id: int):
    _state["favorites"].discard(song_id)
    return {"favorited": False}

# To run: uvicorn playlist_api.server:app --reload
