from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SimilarityService:
    """
    Servicio para detectar PQRS similares usando TF-IDF + Similitud Coseno.
    Agrupa textos por similitud y detecta problemas raíz cuando hay
    más de un umbral definido de PQRS parecidas.
    """

    def __init__(self, similarity_threshold: float = 0.35, alert_threshold: int = 20):
        self.similarity_threshold = similarity_threshold  # Qué tan parecidos deben ser (0-1)
        self.alert_threshold = alert_threshold            # Cuántos para ser problema raíz
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words=None,  # Español no tiene stop_words nativo en sklearn
            ngram_range=(1, 2)
        )

    def find_clusters(self, pqrs_list: list) -> list:
        """
        Recibe una lista de objetos PQRS del repositorio.
        Retorna grupos de PQRS similares con su análisis.
        """
        if len(pqrs_list) < 2:
            return []

        texts = [p.original_text for p in pqrs_list]
        ids = [p.id for p in pqrs_list]

        # Vectorizar textos con TF-IDF
        tfidf_matrix = self.vectorizer.fit_transform(texts)

        # Calcular similitud coseno entre todos los pares
        sim_matrix = cosine_similarity(tfidf_matrix)

        # Agrupar por similitud (clustering simple por grafo)
        visited = set()
        clusters = []

        for i in range(len(texts)):
            if i in visited:
                continue

            # Buscar todos los textos similares a este
            group_indices = []
            for j in range(len(texts)):
                if sim_matrix[i][j] >= self.similarity_threshold:
                    group_indices.append(j)
                    visited.add(j)

            if len(group_indices) >= 2:  # Al menos 2 para ser un grupo
                cluster = {
                    "cluster_size": len(group_indices),
                    "is_root_problem": len(group_indices) >= self.alert_threshold,
                    "priority": "🔴 CRÍTICO" if len(group_indices) >= self.alert_threshold else "🟡 MODERADO",
                    "sample_text": texts[group_indices[0]][:200],
                    "pqrs_ids": [ids[idx] for idx in group_indices],
                    # Extraer palabras clave del grupo
                    "keywords": self._extract_keywords(texts, group_indices)
                }
                clusters.append(cluster)

        # Ordenar por tamaño de grupo (más grandes primero)
        clusters.sort(key=lambda c: c["cluster_size"], reverse=True)
        return clusters

    def _extract_keywords(self, texts: list, indices: list) -> list:
        """Extrae las palabras más relevantes de un grupo de textos similares."""
        group_texts = [texts[i] for i in indices]
        combined = " ".join(group_texts)

        try:
            tfidf = TfidfVectorizer(max_features=10, ngram_range=(1, 2))
            matrix = tfidf.fit_transform([combined])
            feature_names = tfidf.get_feature_names_out()
            scores = matrix.toarray()[0]

            # Ordenar por relevancia
            keyword_scores = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
            return [kw for kw, score in keyword_scores[:5]]
        except:
            return []
