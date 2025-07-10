from datetime import datetime
from typing import List, Optional
from gestor_bdd import GestorBaseDatos
from reclamo import Reclamo
from usuario import Usuario
from departamento import Departamento

class GestorReclamos:

    def __init__(self):
        self.base_de_datos= GestorBaseDatos()

    def crear_adherir(self, usuario:Usuario, contenido:str, nombre_departamento:str, foto_path: Optional[str] = None) -> Reclamo:
        dept = self.base_de_datos.obtener_o_crear_departamento(nombre_departamento)
        reclamos= self.base_de_datos.listar_pendientes(dept.id)
        etiqueta= Reclamo(0, contenido, datetime.utcnow(), "pendiente").clasificar()
        for r in reclamos:
            if r.etiqueta == etiqueta:
                self.base_de_datos.agregar_adherente(r.id, usuario.id) # type: ignore
                return Reclamo(id_reclamo=r.id, contenido=r.contenido, timestamp= r.timestamp, estado=r.estado, departamento= Departamento(id=r.departamento.id, nombre=r.departamento.nombre), adherentes=[usuario]) # type: ignore
    
        nuevo_reclamo= self.base_de_datos.crear_reclamo(contenido=contenido, estado="pendiente", creador_id=usuario.id, departamento_id=dept.id, foto_path=foto_path) # type: ignore
        return Reclamo(id_reclamo=nuevo_reclamo.id, contenido=nuevo_reclamo.contenido, timestamp=nuevo_reclamo.timestamp, estado=nuevo_reclamo.estado, departamento=Departamento(id=nuevo_reclamo.departamento.id, nombre=nuevo_reclamo.departamento.nombre), adherentes=[usuario], foto_path=nuevo_reclamo.foto_path) # type: ignore # type: ignore

    def listar_pendientes(self, nombre_departamento: Optional[str] = None) -> List[Reclamo]:
            dept_id = None
            if nombre_departamento:
                dept = self.base_de_datos.obtener_o_crear_departamento(nombre_departamento)
                dept_id = dept.id

            modelos = self.base_de_datos.listar_pendientes(departamento_id=dept_id)
            return [Reclamo(id_reclamo=m.id, contenido=m.contenido, timestamp=m.timestamp, estado=m.estado, departamento=Departamento(id=m.departamento.id, nombre=m.departamento.nombre), adherentes=[]) for m in modelos] # type: ignore

    def mis_reclamos(self, usuario: Usuario) -> List[Reclamo]:
        modelos = self.base_de_datos.session.query(modelos.ReclamoModelo) # type: ignore
        modelos = modelos.filter(modelos.ReclamoModelo.creador_id == usuario.id).all() # type: ignore
        return [Reclamo(id_reclamo=m.id, contenido=m.contenido, timestamp=m.timestamp, estado=m.estado, departamento=Departamento(id=m.departamento.id, nombre=m.departamento.nombre), adherentes=[]) for m in modelos] # type: ignore

    def cambiar_estado(self, reclamo_id: int, nuevo_estado: str) -> bool:
        return self.base_de_datos.cambiar_estado(reclamo_id, nuevo_estado)

    def estadisticas(self) -> dict[str, int]:
        return self.base_de_datos.estadisticas_por_estado()
    
    def estadisticas_por_departamento(self, nombre_departamento: str) -> dict[str, int]:
        """
        Estadísticas de reclamos sólo de un departamento:
        {'pendiente': N1, 'en_proceso': N2, …}
        """
        # Primero obtén el objeto Departamento para sacar su id
        dept = self.base_de_datos.obtener_o_crear_departamento(nombre_departamento)
        return self.base_de_datos.estadisticas_por_estado(departamento_id=dept.id) # type: ignore

    def top_palabras(self, limit: int = 15) -> List[tuple[str,int]]:
        return self.base_de_datos.top_palabras(limit)
    
    def listar_departamentos(self) -> list[Departamento]:
        modelos = self.base_de_datos.session.query(DepartamentoModelo).all() # type: ignore
        return [Departamento(id=m.id, nombre=m.nombre) for m in modelos] # type: ignore

    def derivar_reclamo(self, reclamo_id: int, nombre_departamento: str) -> bool:
        """
        Cambia el departamento de un reclamo al indicado.
        """
        # Obtener o crear el departamento destino
        depto = self.base_de_datos.obtener_o_crear_departamento(nombre_departamento)
        return self.base_de_datos.cambiar_departamento(reclamo_id, depto.id) # type: ignore
    
    def obtener_reclamo_por_id(self, id_reclamo: int) -> Reclamo:
        from modelos import ReclamoModelo
        m = self.base_de_datos.session.query(ReclamoModelo).get(id_reclamo)
        return Reclamo(id_reclamo=m.id,  contenido=m.contenido, timestamp=m.timestamp, estado=m.estado, departamento=Departamento(id=m.departamento.id, nombre=m.departamento.nombre), adherentes=[Usuario(id=u.id, nombre=u.nombre, apellido=u.apellido, email=u.email, username=u.username, contraseña=u.contraseña, rol=u.rol) for u in m.adherentes]) # type: ignore