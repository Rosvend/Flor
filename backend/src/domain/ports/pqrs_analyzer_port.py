from abc import ABC, abstractmethod


class SentimentAnalyzerPort(ABC):
    @abstractmethod
    def analyze(self, text: str) -> str:
        """Returns sentiment label, e.g. 'NEG (0.99)'."""


class ToxicityDetectorPort(ABC):
    @abstractmethod
    def analyze(self, text: str) -> dict:
        """Returns dict with is_offensive, warning, offensive_words_found."""


class TextCorrectorPort(ABC):
    @abstractmethod
    def improve_text(self, text: str) -> str:
        """Improves the text redaction following Manual V5 guidelines."""


class SimilarityAnalyzerPort(ABC):
    @abstractmethod
    def find_clusters(self, pqrs_list: list[dict]) -> list[dict]:
        """Groups similar PQRS and detects root problems."""

    @abstractmethod
    def find_most_similar(self, target_text: str, candidates: list[dict]) -> tuple[dict, float] | None:
        """
        Finds the most similar PQRS from a list of candidates.
        Returns a tuple of the candidate dict and similarity score (0.0 to 1.0).
        """
        pass
