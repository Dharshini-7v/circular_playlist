from __future__ import annotations
from typing import Optional
from playlist_app.playlist import CircularPlaylist, ListPlaylist


def print_menu() -> None:
    print("\n=== Circular Music Playlist ===")
    print("1. Add song")
    print("2. Remove song")
    print("3. Play current")
    print("4. Next song")
    print("5. Previous song")
    print("6. Enqueue song to play next")
    print("7. Show all songs")
    print("8. Show queue")
    print("9. Show history")
    print("10. Switch playlist implementation (Circular/List)")
    print("0. Exit")


def describe_song(song: Optional[object]) -> str:
    return str(song) if song else "<no song>"


def run_cli() -> None:
    impl = "circular"
    circular = CircularPlaylist()
    linear = ListPlaylist()

    print("Initialized with Circular playlist. Use option 10 to switch.")

    while True:
        print_menu()
        try:
            choice = input("Select an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if choice == "0":
            print("Bye!")
            break

        active = circular if impl == "circular" else linear

        if choice == "1":
            title = input("Title: ").strip()
            artist = input("Artist: ").strip()
            dur_s = input("Duration in seconds (optional): ").strip()
            try:
                dur = int(dur_s) if dur_s else 0
            except ValueError:
                dur = 0
            song = active.add_song(title, artist, dur)
            print(f"Added: {song} (id={song.id})")

        elif choice == "2":
            sid = input("Song id to remove: ").strip()
            try:
                ok = active.remove_song(int(sid))
                print("Removed" if ok else "Song not found")
            except ValueError:
                print("Invalid id")

        elif choice == "3":
            print("Playing:", describe_song(active.play()))

        elif choice == "4":
            print("Next:", describe_song(active.next()))

        elif choice == "5":
            print("Previous:", describe_song(active.previous()))

        elif choice == "6":
            sid = input("Song id to enqueue next: ").strip()
            try:
                ok = active.enqueue_next(int(sid))
                print("Enqueued" if ok else "Song not found")
            except ValueError:
                print("Invalid id")

        elif choice == "7":
            songs = active.list_songs()
            if not songs:
                print("No songs")
            else:
                for s in songs:
                    print(f"- {s} (id={s.id})")

        elif choice == "8":
            q = list(active.up_next)
            if not q:
                print("Queue empty")
            else:
                for s in q:
                    print(f"- {s} (id={s.id})")

        elif choice == "9":
            h = list(active.history)
            if not h:
                print("History empty")
            else:
                for s in h:
                    print(f"- {s} (id={s.id})")

        elif choice == "10":
            impl = "list" if impl == "circular" else "circular"
            print(f"Switched to {impl.capitalize()} playlist")

        else:
            print("Invalid choice")


if __name__ == "__main__":
    run_cli()
