from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from collections import Counter
from typing import Optional
from modelos import ReclamoModelo
import io
import matplotlib.pyplot as plt
import base64
import modelos  
from base_de_datos import Base

class GestorBaseDatos:
    def __init__(self, base_de_datos_url: str = "sqlite:///tp3.base_de_datos"):
        self.engine = create_engine(base_de_datos_url, connect_args={"check_same_thread": False})
        Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self.session = Session()
        Base.metadata.create_all(self.engine)


    def crear_usuario(self, nombre, apellido, email, username, contraseña, rol):
        usuario = modelos.UsuarioModelo(nombre=nombre, apellido=apellido, email=email, username=username, contraseña=contraseña, rol=rol)
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)
        return usuario

    def obtener_usuario_por_username(self, username):
        return (self.session.query(modelos.UsuarioModelo).filter(modelos.UsuarioModelo.username == username).first())

    def obtener_usuario_por_email(self, email):
        return (
            self.session.query(modelos.UsuarioModelo).filter(modelos.UsuarioModelo.email == email).first())

    def obtener_o_crear_departamento(self, nombre):
        dept = (self.session.query(modelos.DepartamentoModelo).filter(modelos.DepartamentoModelo.nombre == nombre).first())
        if not dept:
            dept = modelos.DepartamentoModelo(nombre=nombre)
            self.session.add(dept)
            self.session.commit()
            self.session.refresh(dept)
        return dept

    def crear_reclamo(self, contenido, estado, creador_id, departamento_id):
        reclamo = modelos.ReclamoModelo(contenido=contenido, timestamp=datetime.utcnow(), estado=estado, creador_id=creador_id, departamento_id=departamento_id)
        self.session.add(reclamo)
        self.session.commit()
        self.session.refresh(reclamo)
        return reclamo

    def listar_pendientes(self, departamento_id=None):
        query = (self.session.query(modelos.ReclamoModelo).filter(modelos.ReclamoModelo.estado == "pendiente"))
        if departamento_id is not None:
            query = query.filter(modelos.ReclamoModelo.departamento_id == departamento_id)
        return query.all()

    def agregar_adherente(self, reclamo_id, usuario_id):
        recl = self.session.query(modelos.ReclamoModelo).get(reclamo_id)
        if recl and all(u.id != usuario_id for u in recl.adherentes):
            usuario = self.session.query(modelos.UsuarioModelo).get(usuario_id)
            recl.adherentes.append(usuario)
            self.session.commit()
            return True
        return False

    def cambiar_estado(self, reclamo_id, nuevo_estado):
        recl = self.session.query(modelos.ReclamoModelo).get(reclamo_id)
        if recl:
            recl.estado = nuevo_estado
            self.session.commit()
            return True
        return False

    def estadisticas_por_estado(
            self,
            departamento_id: Optional[int] = None
        ) -> dict[str,int]:
            """
            Si departamento_id es None, cuenta todos los reclamos;
            si viene un id, solo los de ese departamento.
            """
            query = (
                self.session
                    .query(ReclamoModelo.estado, func.count())
                    .group_by(ReclamoModelo.estado)
            )
            if departamento_id is not None:
                query = query.filter(ReclamoModelo.departamento_id == departamento_id)

            filas = query.all()  # List[Tuple[str,int]]
            return {estado: cuenta for estado, cuenta in filas}

    def top_palabras(self, limit=15):
        textos = [r.contenido for r in self.session.query(modelos.ReclamoModelo).all()]
        counter = Counter()
        for texto in textos:
            counter.update(texto.lower().split())
        return counter.most_common(limit)
    
    def cambiar_departamento(self, reclamo_id: int, nuevo_depto_id: int) -> bool:
        recl = self.session.query(ReclamoModelo).get(reclamo_id)
        if not recl:
            return False
        recl.departamento_id = nuevo_depto_id
        self.session.commit()
        return True
    
    def generar_pie(self,
                    estadisticas: dict[str,int],
                    size: tuple[int,int] = (4,4)
                   ) -> str:
        """
        Genera un pie chart con Matplotlib a partir de un dict
        Devuelve la imagen codificada en Base64 para incrustar en HTML.
        """
        # 1) Prepara datos
        labels = list(estadisticas.keys())
        counts = list(estadisticas.values())

        # 2) Dibuja con Matplotlib
        fig, ax = plt.subplots(figsize=size)
        ax.pie(counts,
               labels=labels,
               autopct='%1.1f%%',
               startangle=90)
        ax.axis('equal')  # círculo perfecto

        # 3) Guarda a un buffer en memoria
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)

        # 4) Codifica a Base64
        img_b64 = base64.b64encode(buf.read()).decode('ascii')
        return img_b64