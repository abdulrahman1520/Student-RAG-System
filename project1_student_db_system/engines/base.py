from typing import Protocol

class ChatEngine(Protocol):
    def answer(self, query: str) -> str:
        ...