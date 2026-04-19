from sentence_transformers import SentenceTransformer, util
import torch

from src.domain.ports.department_router_port import DepartmentRouterPort
from src.domain.ports.department_repository_port import DepartmentRepositoryPort
from src.domain.entities.department import Department


class SemanticDepartmentRouter(DepartmentRouterPort):
    def __init__(
        self, 
        repository: DepartmentRepositoryPort,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ) -> None:
        self._repository = repository
        self._model = SentenceTransformer(model_name)
        
        # Precomputar los embeddings de todas las secretarías al instanciar
        self._departments = self._repository.list_all()
        # Construimos el texto a embeber: nombre + alcance
        scopes_text = [
            f"{d.name}. {d.scope}" for d in self._departments
        ]
        
        if scopes_text:
            self._dept_embeddings = self._model.encode(scopes_text, convert_to_tensor=True)
        else:
            self._dept_embeddings = None

    def route(self, text: str) -> Department | None:
        if not self._departments or self._dept_embeddings is None:
            return None
            
        if not text or len(text.strip()) < 10:
            return None

        try:
            # truncate text to avoid max length errors
            truncated_text = text[:1000]
            
            # Generar embedding de la PQRS
            query_embedding = self._model.encode(truncated_text, convert_to_tensor=True)
            
            # Calcular similitud coseno con todas las secretarías
            cosine_scores = util.cos_sim(query_embedding, self._dept_embeddings)[0]
            
            # Obtener el índice del mayor score
            best_match_idx = torch.argmax(cosine_scores).item()
            score = cosine_scores[best_match_idx].item()
            
            # Umbral mínimo de similitud para evitar enrutamientos basura
            if score > 0.15:
                return self._departments[best_match_idx]
            return None
            
        except Exception as e:
            print(f"Error enruutando PQRS: {e}")
            return None
