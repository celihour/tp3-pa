from typing import List
from reclamo import Reclamo

class Departamento:
    def __init__(self, id_departamento: int, nombre: str):
        self.id_departamento = id_departamento
        self.nombre = nombre
        self._reclamos: List[Reclamo] = []

    def ver_reclamos(self):
        return self._reclamos

    def agregar_reclamo(self, reclamo: Reclamo):
        self._reclamos.append(reclamo)

    def __repr__(self) -> str:
        return f"<Departamento {self.id_departamento} - {self.nombre}>"
