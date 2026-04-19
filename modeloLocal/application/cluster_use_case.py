import os
from ..infrastructure.similarity_service import SimilarityService
from ..infrastructure.repository import PQRSRepository

class ClusterPQRSUseCase:
    """Caso de uso para encontrar PQRS similares y detectar problemas raíz."""

    def __init__(self):
        self.similarity_service = SimilarityService(
            similarity_threshold=0.35,
            alert_threshold=20
        )
        self.repository = PQRSRepository(os.getenv("DATABASE_URL", "sqlite:///./pqrs.db"))

    def execute(self):
        # 1. Obtener todas las PQRS
        all_pqrs = self.repository.get_all()

        if len(all_pqrs) < 2:
            return {
                "total_pqrs": len(all_pqrs),
                "clusters_found": 0,
                "root_problems": 0,
                "clusters": [],
                "message": "Se necesitan al menos 2 PQRS para analizar similitudes."
            }

        # 2. Encontrar clusters
        clusters = self.similarity_service.find_clusters(all_pqrs)

        root_problems = [c for c in clusters if c["is_root_problem"]]

        return {
            "total_pqrs": len(all_pqrs),
            "clusters_found": len(clusters),
            "root_problems": len(root_problems),
            "clusters": clusters,
            "message": (
                f"⚠️ Se detectaron {len(root_problems)} problema(s) raíz "
                f"con más de 20 PQRS similares. Requieren atención inmediata."
                if root_problems else
                "No se detectaron problemas raíz (ningún grupo supera las 20 PQRS similares)."
            )
        }
