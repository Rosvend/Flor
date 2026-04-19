import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.domain.ports.pqrs_analyzer_port import SimilarityAnalyzerPort


class TfidfSimilarityAnalyzer(SimilarityAnalyzerPort):
    """Agrupación de PQRS similares usando TF-IDF + Similitud Coseno."""

    def __init__(
        self, similarity_threshold: float = 0.35, alert_threshold: int = 20
    ) -> None:
        self._sim_threshold = similarity_threshold
        self._alert_threshold = alert_threshold

    def find_clusters(self, pqrs_list: list[dict]) -> list[dict]:
        if len(pqrs_list) < 2:
            return []

        # Extraer y filtrar textos que no estén vacíos
        raw_texts = [
            p.get("text", p.get("original_text", p.get("contenido", ""))) 
            for p in pqrs_list
        ]
        valid_indices = [i for i, t in enumerate(raw_texts) if len(str(t).strip()) > 5]
        
        if len(valid_indices) < 2:
            return []

        texts = [str(raw_texts[i]) for i in valid_indices]
        ids = [valid_indices[i] for i in range(len(valid_indices))]

        try:
            vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(texts)
            sim_matrix = cosine_similarity(tfidf_matrix)
        except ValueError:
            # Captura "empty vocabulary" si los textos no tienen palabras útiles
            return []

        visited: set[int] = set()
        clusters: list[dict] = []

        for i in range(len(texts)):
            if i in visited:
                continue
            group = [
                j for j in range(len(texts))
                if sim_matrix[i][j] >= self._sim_threshold
            ]
            for j in group:
                visited.add(j)

            if len(group) >= 2:
                clusters.append({
                    "cluster_size": len(group),
                    "is_root_problem": len(group) >= self._alert_threshold,
                    "priority": (
                        "🔴 CRÍTICO" if len(group) >= self._alert_threshold
                        else "🟡 MODERADO"
                    ),
                    "sample_text": texts[group[0]][:200],
                    "pqrs_ids": [ids[idx] for idx in group],
                    "keywords": self._extract_keywords(texts, group),
                })

        clusters.sort(key=lambda c: c["cluster_size"], reverse=True)
        return clusters

    @staticmethod
    def _extract_keywords(texts: list[str], indices: list[int]) -> list[str]:
        combined = " ".join(texts[i] for i in indices)
        try:
            vec = TfidfVectorizer(max_features=10, ngram_range=(1, 2))
            matrix = vec.fit_transform([combined])
            names = vec.get_feature_names_out()
            scores = matrix.toarray()[0]
            ranked = sorted(zip(names, scores), key=lambda x: x[1], reverse=True)
            return [kw for kw, _ in ranked[:5]]
        except Exception:
            return []

    def find_most_similar(self, target_text: str, candidates: list[dict]) -> tuple[dict, float] | None:
        if not target_text or len(target_text.strip()) < 5 or not candidates:
            return None

        # Extract texts from candidates
        cand_texts = []
        valid_candidates = []
        for c in candidates:
            t = c.get("text", c.get("original_text", c.get("contenido", "")))
            if t and len(str(t).strip()) > 5:
                cand_texts.append(str(t))
                valid_candidates.append(c)

        if not valid_candidates:
            return None

        all_texts = [target_text] + cand_texts

        try:
            vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            # The first row is the target_text, the rest are candidates
            sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            best_idx = np.argmax(sim_scores)
            best_score = float(sim_scores[best_idx])
            
            if best_score > 0:
                return valid_candidates[best_idx], best_score
            return None
        except Exception:
            return None
