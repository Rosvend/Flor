from abc import ABC, abstractmethod

from src.domain.entities.department import Department


class DepartmentRouterPort(ABC):
    @abstractmethod
    def route(self, text: str) -> Department | None:
        """
        Analiza el texto de una PQRSD y determina a qué Secretaría o Departamento
        (Department) debe ser enrutado según su alcance o funciones.
        """
