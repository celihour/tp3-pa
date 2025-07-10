from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey, Table)
from sqlalchemy.orm import relationship
from base_de_datos import Base

adherentes= Table("adherentes", Base.metadata, Column("reclamo_id",Integer, ForeignKey("reclamos.id"), primary_key=True), Column("usuario_id",Integer,ForeignKey("usuarios.id"),primary_key=True))

class UsuarioModelo(Base):
    __tablename__= "usuarios"
    id= Column(Integer, primary_key=True, index=True)
    nombre= Column(String, nullable=False)
    apellido= Column(String, nullable=False)
    email= Column(String, unique=True, nullable=False, index=True)
    username= Column(String, unique=True, nullable=False, index=True)
    contraseña= Column(String, nullable=False)
    rol= Column(String, nullable=False)

    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=True)
    departamento    = relationship("DepartamentoModelo", back_populates="jefes")

    reclamos_creados= relationship("ReclamoModelo", back_populates="creador", cascade="all, delete-orphan")
    reclamos_adheridos= relationship("ReclamoModelo",secondary=adherentes, back_populates="adherentes")

class DepartamentoModelo(Base):
    __tablename__= "departamentos"
    id       = Column(Integer, primary_key=True, index=True)
    nombre   = Column(String, unique=True, nullable=False)

    reclamos = relationship("ReclamoModelo", back_populates="departamento")
    jefes = relationship("UsuarioModelo", back_populates="departamento")

class ReclamoModelo(Base):
    __tablename__ = "reclamos"
    id             = Column(Integer, primary_key=True, index=True)
    contenido      = Column(String, nullable=False)
    timestamp      = Column(DateTime, nullable=False)
    estado         = Column(String, nullable=False)
    creador_id     = Column(Integer, ForeignKey("usuarios.id"))
    departamento_id= Column(Integer, ForeignKey("departamentos.id"))
    foto_path = Column(String, nullable=True)

    creador       = relationship("UsuarioModelo", back_populates="reclamos_creados")
    departamento  = relationship("DepartamentoModelo", back_populates="reclamos")
    adherentes    = relationship("UsuarioModelo", secondary=adherentes, back_populates="reclamos_adheridos")