import sys
sys.path.insert(0, "src")

from gestor_bdd import GestorBaseDatos
from gestor_usuario import GestorUsuarios

def main():
    db  = GestorBaseDatos()
    gu  = GestorUsuarios()

    for dept_name in ["Soporte TI", "Infraestructura", "Secretaría Técnica"]:
        db.obtener_o_crear_departamento(dept_name)

    print("Creando jefes de departamento…")
    jefe1 = gu.registrar_usuario(
        nombre="Bugs", apellido="Bunny",
        email="bugs.bunny@looneytunes.com",
        username="bugs",
        contraseña="zanahoria", contraseña_repetida="zanahoria",
        rol="jefe_departamento")
    print(f"  ✓ Jefe mantenimiento: {jefe1.username}")

    gu.asignar_departamento(jefe1, "mantenimiento") # type: ignore
    print(f"Asignado {jefe1.username} a Mantenimiento")


    jefe2 = gu.registrar_usuario(
        nombre="Speedy", apellido="Gonzales",
        email="speedy.gonzales@looneytunes.com",
        username="speedy",
        contraseña="sombrero", contraseña_repetida="sombrero",
        rol="jefe_departamento")
    print(f" Jefe creado: {jefe2.username}")

    gu.asignar_departamento(jefe2, "alumnado")# type: ignore
    print(f"Asignado {jefe2.username} a Alumnado")

    sec = gu.registrar_usuario(
        nombre="Ariel", apellido="Princesa",
        email="lasirenita@disney.com",
        username="la.sirenita",
        contraseña="flounder", contraseña_repetida="flounder",
        rol="secretario_tecnico")
    print(f"Secretario ténico: {sec.username}" )
    
    print("🎉 ¡Semillas cargadas con éxito!")

if __name__ == "__main__":
    main()