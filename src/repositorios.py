from sqlalchemy.orm import Session
from base_de_datos import SessionLocal
from modelos import UsuarioModelo, DepartamentoModelo, ReclamoModelo
from datetime import datetime
from sqlalchemy import func 
from collections import Counter

class repoUsuario: 
    def __init__(self):
        self.base_de_datos: Session = SessionLocal()

    def añadir(self, user:UsuarioModelo) -> UsuarioModelo:
        self.base_de_datos.add(user)
        self.base_de_datos.commit()
        self.base_de_datos.refresh(user)
        return user
    
    def get_username(self, username:str):
        return(self.base_de_datos.query(UsuarioModelo).filter(UsuarioModelo.username==username).first())
    
    def get_email(self, email:str):
        return(self.base_de_datos.query(UsuarioModelo).filter(UsuarioModelo.email==email).first())
    
class repoDepartamento:
    def __init__(self):
        self.base_de_datos: Session= SessionLocal()
    
    def get_crear(self, nombre: str):
        dept=(self.base_de_datos.query(DepartamentoModelo).filter(DepartamentoModelo.nombre == nombre).first())
        if not dept:
            dept= DepartamentoModelo(nombre=nombre)
            self.base_de_datos.add(dept)
            self.base_de_datos.commit()
            self.base_de_datos.refresh(dept)
        return dept
    
class repoReclamo:
    def __init__(self):
        self.base_de_datos: Session= SessionLocal()

    def añadir(self, contenido: str, estado: str, creador, departamento):
        recl= ReclamoModelo(contendio=contenido, timestamp=datetime.utcnow(), estado=estado, creador=creador, departamento=departamento)
        self.base_de_datos.add(recl)
        self.base_de_datos.commit()
        self.base_de_datos.refresh(recl)
        return recl
    
    def lista_pendientes(self, departamento= None):
        query= self.base_de_datos.query(ReclamoModelo).filter(ReclamoModelo.estado == "pendiente")
        if departamento:
            query=query.filter(ReclamoModelo.departamento_id == departamento.id)
        return query.all()
    
    def agregar_adherente(self, reclamo_id: int, usuario):
        recl= self.base_de_datos.query(ReclamoModelo).get(reclamo_id)
        if recl and usuario not in recl.adherentes:
            recl.adherentes.append(usuario)
            self.base_de_datos.commit()
            return True
        return False
    
    def cambiar_estado(self, reclamo_id: int, nuevo_estado: str):
        recl= self.base_de_datos.query(ReclamoModelo).get(reclamo_id)
        if recl:
            recl.estado= nuevo_estado
            return True
        return False
    
    def estadisticas_estados(self) -> dict[str, int]:
        filas=(self.base_de_datos.query(ReclamoModelo.estado, func.count()).group_by(ReclamoModelo.estado).all())
        return {estado: count for estado, count in filas}

    def limite_palabras(self, limit=15):
        textos= [r.contenido for r in self.base_de_datos.query(ReclamoModelo).all()]
        counter= Counter()
        for t in textos:
            counter.update(t.lower().split())
        return counter.most_common(limit)
    

