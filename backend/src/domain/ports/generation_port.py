from abc import ABC, abstractmethod


class GenerationPort(ABC):
    @abstractmethod
    def generate(self, system: str, user: str, max_tokens: int = 512) -> str: ...
