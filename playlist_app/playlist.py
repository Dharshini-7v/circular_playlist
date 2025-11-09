from __future__ import annotations
from typing import Optional
from .models import Song
from .structures import Stack, Queue, CircularDoublyLinkedList, _Node


class CircularPlaylist:
    def __init__(self) -> None:
        self._list: CircularDoublyLinkedList[Song] = CircularDoublyLinkedList()
        self._current: Optional[_Node[Song]] = None
        self.history: Stack[Song] = Stack()
        self.up_next: Queue[Song] = Queue()
        self._next_song_id = 1

    def add_song(self, title: str, artist: str, duration_sec: int = 0, audio_url: str | None = None) -> Song:
        song = Song(self._next_song_id, title, artist, duration_sec, audio_url)
        self._next_song_id += 1
        self._list.append(song)
        if self._current is None:
            # Set current to head when the first song is added
            head_value = self._list.head()
            if head_value is not None:
                self._current = self._list.find_node(head_value)
        return song

    def remove_song(self, song_id: int) -> bool:
        if self._list.is_empty():
            return False
        # if removing current, advance first
        if self._current and self._current.value.id == song_id:
            self.next()
        # find by id
        node = self._current
        if not node:
            return False
        for _ in range(len(self._list)):
            if node.value.id == song_id:
                removed = self._list.remove(node.value)
                return removed
            node = self._list.node_after(node)
        return False

    def play(self) -> Optional[Song]:
        if self._current:
            return self._current.value
        return None

    def next(self) -> Optional[Song]:
        # priority to up_next queue
        queued = self.up_next.dequeue()
        if queued:
            if self._current:
                self.history.push(self._current.value)
            # move current to a node with this song if exists; otherwise append
            node = self._list.find_node(queued)
            if node is None:
                self._list.append(queued)
                head_val = self._list.head()
                node = self._list.find_node(head_val)  # fallback to some node
            self._current = node
            return queued

        if self._current is None:
            head_val = self._list.head()
            if head_val is None:
                return None
            self._current = self._list.find_node(head_val)
            return self._current.value if self._current else None

        self.history.push(self._current.value)
        self._current = self._list.node_after(self._current)
        return self._current.value

    def previous(self) -> Optional[Song]:
        # Prefer history if available
        prev = self.history.pop()
        if prev:
            node = self._list.find_node(prev)
            if node:
                self._current = node
                return prev

        if self._current is None:
            head_val = self._list.head()
            if head_val is None:
                return None
            self._current = self._list.find_node(head_val)
            return self._current.value if self._current else None

        self._current = self._list.node_before(self._current)
        return self._current.value

    def enqueue_next(self, song_id: int) -> bool:
        node = self._current
        if not node:
            # start from head if current is not set yet
            head_val = self._list.head()
            node = self._list.find_node(head_val) if head_val is not None else None
            if not node:
                return False
        for _ in range(len(self._list)):
            if node.value.id == song_id:
                self.up_next.enqueue(node.value)
                return True
            node = self._list.node_after(node)
        return False

    def list_songs(self) -> list[Song]:
        if self._list.is_empty():
            return []
        head_val = self._list.head()
        node = self._list.find_node(head_val) if head_val else None
        if not node:
            return []
        return list(self._list.iter_forward(start=node))


class ListPlaylist:
    def __init__(self) -> None:
        self._songs: list[Song] = []
        self._pos = -1
        self.history: Stack[Song] = Stack()
        self.up_next: Queue[Song] = Queue()
        self._next_song_id = 1

    def add_song(self, title: str, artist: str, duration_sec: int = 0, audio_url: str | None = None) -> Song:
        song = Song(self._next_song_id, title, artist, duration_sec, audio_url)
        self._next_song_id += 1
        self._songs.append(song)
        if self._pos == -1:
            self._pos = 0
        return song

    def remove_song(self, song_id: int) -> bool:
        for i, s in enumerate(self._songs):
            if s.id == song_id:
                del self._songs[i]
                if self._pos >= len(self._songs):
                    self._pos = len(self._songs) - 1
                return True
        return False

    def play(self) -> Optional[Song]:
        if 0 <= self._pos < len(self._songs):
            return self._songs[self._pos]
        return None

    def next(self) -> Optional[Song]:
        queued = self.up_next.dequeue()
        if queued:
            if 0 <= self._pos < len(self._songs):
                self.history.push(self._songs[self._pos])
            self._songs.append(queued)
            self._pos = len(self._songs) - 1
            return queued
        if not self._songs:
            return None
        if 0 <= self._pos < len(self._songs):
            self.history.push(self._songs[self._pos])
        self._pos = (self._pos + 1) % len(self._songs)
        return self._songs[self._pos]

    def previous(self) -> Optional[Song]:
        prev = self.history.pop()
        if prev:
            try:
                idx = next(i for i, s in enumerate(self._songs) if s.id == prev.id)
                self._pos = idx
                return prev
            except StopIteration:
                pass
        if not self._songs:
            return None
        self._pos = (self._pos - 1) % len(self._songs)
        return self._songs[self._pos]

    def enqueue_next(self, song_id: int) -> bool:
        for s in self._songs:
            if s.id == song_id:
                self.up_next.enqueue(s)
                return True
        return False

    def list_songs(self) -> list[Song]:
        return list(self._songs)
