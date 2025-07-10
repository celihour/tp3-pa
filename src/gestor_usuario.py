from gestor_bdd import GestorBaseDatos
from usuario import Usuario
from modelos import UsuarioModelo

class GestorUsuarios:
    def __init__(self):
        self.base_de_datos = GestorBaseDatos()

    def registrar_usuario(self, nombre: str, apellido: str, email: str, username: str, contraseña: str, contraseña_repetida: str, rol: str) -> Usuario:
        if contraseña != contraseña_repetida:
            raise ValueError("Las contraseñas no coinciden")
        if self.base_de_datos.obtener_usuario_por_email(email):
            raise ValueError("El email ya está registrado")
        if self.base_de_datos.obtener_usuario_por_username(username):
            raise ValueError("El nombre de usuario ya existe")

        modelo = self.base_de_datos.crear_usuario(nombre=nombre, apellido=apellido, email=email, username=username, contraseña=contraseña, rol=rol)

        return Usuario(id_usuario=modelo.id, nombre=modelo.nombre, apellido=modelo.apellido, email=modelo.email, username=modelo.username, contraseña=modelo.contraseña, rol=modelo.rol) # type: ignore

    def registrar_jefe_departamento(self, nombre: str, apellido: str, email: str, username: str, contraseña: str, contraseña_repetida: str, nombre_departamento: str) -> Usuario:
        user = self.registrar_usuario(nombre, apellido, email, username, contraseña, contraseña_repetida, rol="jefe_departamento")
        dept = self.base_de_datos.obtener_o_crear_departamento(nombre_departamento)
        modelo = self.base_de_datos.session.query(UsuarioModelo).get(user.id_usuario)
        modelo.departamento_id = dept.id # type: ignore
        self.base_de_datos.session.commit()
        return user

    def registrar_secretario_tecnico(self, nombre: str, apellido: str, email: str, username: str, contraseña: str, contraseña_repetida: str) -> Usuario:
        return self.registrar_usuario(nombre, apellido, email, username, contraseña, contraseña_repetida, rol="secretario_tecnico")

    def login(self, username: str, contraseña: str) -> Usuario | None:
        modelo = self.base_de_datos.obtener_usuario_por_username(username)
        if modelo and modelo.contraseña == contraseña: # type: ignore
            return Usuario(id_usuario=modelo.id, nombre=modelo.nombre, apellido=modelo.apellido, email=modelo.email, username=modelo.username, contraseña=modelo.contraseña, rol=modelo.rol) # type: ignore
        return None
    
    def obtener_por_id(self, id_usuario: int) -> Usuario | None:
        model = self.base_de_datos.session.query(UsuarioModelo).get(id_usuario)
        if not model:
            return None
        return Usuario(id_usuario=model.id, nombre=model.nombre, apellido=model.apellido, email=model.email, username=model.username, contraseña=model.contraseña, rol=model.rol)
    
    def asignar_departamento(self, usuario: UsuarioModelo, nombre_departamento: str) -> None:
        from modelos import DepartamentoModelo
        dept = self.base_de_datos.session.query(DepartamentoModelo).filter_by(nombre=nombre_departamento).first()
        if not dept:
            dept = self.base_de_datos.obtener_o_crear_departamento(nombre_departamento)
        usuario.departamento = dept
        self.base_de_datos.session.commit()

    

