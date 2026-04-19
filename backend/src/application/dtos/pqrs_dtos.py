from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProcessPQRSInput:
    text: str


@dataclass
class ProcessPQRSOutput:
    original_text: str
    improved_text: str
    sentiment: str
    is_offensive: bool
    toxicity_warning: Optional[str]
    offensive_words: list[str] = field(default_factory=list)
    tipo_sugerido: Optional[str] = None
    secretaria_asignada: Optional[str] = None


@dataclass
class ClusterItem:
    cluster_size: int
    is_root_problem: bool
    priority: str
    sample_text: str
    pqrs_ids: list[int]
    keywords: list[str]


@dataclass
class ClusterPQRSOutput:
    total_pqrs: int
    clusters_found: int
    root_problems: int
    message: str
    clusters: list[ClusterItem] = field(default_factory=list)
