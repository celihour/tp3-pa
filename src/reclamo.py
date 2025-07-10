from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from clasificador_externo.modules.classifier import ClaimsClassifier
from clasificador_externo.modules.create_csv import crear_csv
from pathlib import Path

if TYPE_CHECKING:
    from departamento import Departamento
    from usuario import Usuario

base_direct= Path(__file__).parent
json_path= base_direct / "clasificador_externo" / "data"/ "frases.json"
_datos_tp = crear_csv(str(json_path))
_clf_global = ClaimsClassifier().fit(_datos_tp["reclamo"], _datos_tp["etiqueta"]) # type: ignore

class Reclamo:

    estado= ["invalido", "pendiente", "en_proceso", "resuelto"]

    def __init__(self, id_reclamo: int, contenido: str, timestamp: datetime, estado: str, departamento: Optional["Departamento"] = None, adherentes: Optional[List["Usuario"]] = None, creador: Optional["Usuario"] = None):
        if estado not in Reclamo.estado:
            raise ValueError(f"Estado inválido: {estado}")
        self.id_reclamo = id_reclamo
        self.contenido = contenido
        self.timestamp = timestamp
        self.estado = estado
        self.departamento = departamento
        self.adherentes = adherentes or []
        self.creador = creador

    def clasificar(self) -> str:
        return _clf_global.clasificar([self.contenido])[0]

    def agregar_adherente(self, usuario: "Usuario") -> bool:
        if usuario in self.adherentes:
            return False
        self.adherentes.append(usuario)
        return True

    def cambiar_estado(self, nuevo_estado: str) -> None:
        if nuevo_estado not in Reclamo.estado:
            raise ValueError(f"Estado inválido: {nuevo_estado}")
        self.estado= nuevo_estado
    