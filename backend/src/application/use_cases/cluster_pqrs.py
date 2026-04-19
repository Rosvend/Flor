from src.domain.ports.pqrs_analyzer_port import SimilarityAnalyzerPort
from src.domain.ports.raw_data_lake import RawDataLakePort
from src.application.dtos.pqrs_dtos import ClusterPQRSOutput


class ClusterPQRS:
    """Agrupa PQRS similares desde el data lake y detecta problemas raíz."""

    def __init__(
        self,
        similarity_analyzer: SimilarityAnalyzerPort,
        data_lake: RawDataLakePort,
    ) -> None:
        self._similarity = similarity_analyzer
        self._data_lake = data_lake

    def execute(self, pqrs_records: list[dict]) -> ClusterPQRSOutput:
        if len(pqrs_records) < 2:
            return ClusterPQRSOutput(
                total_pqrs=len(pqrs_records),
                clusters_found=0,
                root_problems=0,
                message="Se necesitan al menos 2 PQRS para analizar similitudes.",
            )

        clusters = self._similarity.find_clusters(pqrs_records)
        root_problems = [c for c in clusters if c["is_root_problem"]]

        return ClusterPQRSOutput(
            total_pqrs=len(pqrs_records),
            clusters_found=len(clusters),
            root_problems=len(root_problems),
            clusters=clusters,
            message=(
                f"⚠️ Se detectaron {len(root_problems)} problema(s) raíz "
                f"con más de 20 PQRS similares."
                if root_problems
                else "No se detectaron problemas raíz."
            ),
        )
