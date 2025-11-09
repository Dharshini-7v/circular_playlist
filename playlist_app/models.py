from dataclasses import dataclass


@dataclass
class Song:
    id: int
    title: str
    artist: str
    duration_sec: int = 0
    audio_url: str | None = None

    def __str__(self) -> str:
        mm = self.duration_sec // 60
        ss = self.duration_sec % 60
        dur = f" {mm:02d}:{ss:02d}" if self.duration_sec else ""
        return f"{self.title} - {self.artist}{dur}"
