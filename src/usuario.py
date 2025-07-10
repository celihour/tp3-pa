from reclamo import Reclamo
from departamento import Departamento

class Usuario:

    roles= ["usuario_final", "jefe_departamento", "secretario_tecnico", ]

    def __init__(self, id_usuario: int, nombre: str, apellido: str, email: str, username: str, contraseña: str, rol: str):
        if rol not in Usuario.roles:
            raise ValueError(f"Rol inválido: {rol}")
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.username = username
        self.contraseña = contraseña
        self.rol = rol
    
    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre}{self.apellido}"
    
    def es_administrador(self) -> bool:
        return self.rol in {"jefe_departamento", "secretario_tenico"}
