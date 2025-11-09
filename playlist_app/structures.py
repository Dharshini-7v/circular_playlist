from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, Optional, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._data: list[T] = []

    def push(self, item: T) -> None:
        self._data.append(item)

    def pop(self) -> Optional[T]:
        return self._data.pop() if self._data else None

    def peek(self) -> Optional[T]:
        return self._data[-1] if self._data else None

    def is_empty(self) -> bool:
        return not self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return reversed(self._data)


class Queue(Generic[T]):
    def __init__(self) -> None:
        self._data: list[T] = []
        self._head = 0

    def enqueue(self, item: T) -> None:
        self._data.append(item)

    def dequeue(self) -> Optional[T]:
        if self._head < len(self._data):
            item = self._data[self._head]
            self._head += 1
            # compact occasionally
            if self._head > 32 and self._head > len(self._data) // 2:
                self._data = self._data[self._head :]
                self._head = 0
            return item
        return None

    def peek(self) -> Optional[T]:
        return self._data[self._head] if self._head < len(self._data) else None

    def is_empty(self) -> bool:
        return self._head >= len(self._data)

    def __len__(self) -> int:
        return len(self._data) - self._head

    def __iter__(self) -> Iterator[T]:
        for i in range(self._head, len(self._data)):
            yield self._data[i]


@dataclass
class _Node(Generic[T]):
    value: T
    prev: Optional["_Node[T]"] = None
    next: Optional["_Node[T]"] = None


class CircularDoublyLinkedList(Generic[T]):
    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        self._head: Optional[_Node[T]] = None
        self._size = 0
        if items:
            for item in items:
                self.append(item)

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def head(self) -> Optional[T]:
        return self._head.value if self._head else None

    def append(self, value: T) -> None:
        node = _Node(value)
        if not self._head:
            node.prev = node.next = node
            self._head = node
        else:
            tail = self._head.prev  # type: ignore[assignment]
            assert tail is not None
            node.prev = tail
            node.next = self._head
            tail.next = node
            self._head.prev = node
        self._size += 1

    def remove(self, value: T) -> bool:
        if not self._head:
            return False
        curr = self._head
        for _ in range(self._size):
            if curr.value == value:
                if self._size == 1:
                    self._head = None
                else:
                    curr.prev.next = curr.next  # type: ignore[union-attr]
                    curr.next.prev = curr.prev  # type: ignore[union-attr]
                    if curr is self._head:
                        self._head = curr.next
                self._size -= 1
                return True
            curr = curr.next  # type: ignore[assignment]
        return False

    def find_node(self, value: T) -> Optional[_Node[T]]:
        if not self._head:
            return None
        curr = self._head
        for _ in range(self._size):
            if curr.value == value:
                return curr
            curr = curr.next  # type: ignore[assignment]
        return None

    def iter_forward(self, start: Optional[_Node[T]] = None) -> Iterator[T]:
        if self._size == 0:
            return iter(())
        node = start or self._head
        assert node is not None
        yield node.value
        curr = node.next
        while curr is not None and curr is not node:
            yield curr.value
            curr = curr.next

    def iter_backward(self, start: Optional[_Node[T]] = None) -> Iterator[T]:
        if self._size == 0:
            return iter(())
        node = start or self._head
        assert node is not None
        yield node.value
        curr = node.prev
        while curr is not None and curr is not node:
            yield curr.value
            curr = curr.prev

    def node_after(self, node: _Node[T]) -> _Node[T]:
        assert node.next is not None
        return node.next

    def node_before(self, node: _Node[T]) -> _Node[T]:
        assert node.prev is not None
        return node.prev
