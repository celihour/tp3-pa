from datetime import datetime
from usuario import Usuario
from gestor_usuario import GestorUsuarios
from departamento import Departamento
from reclamo import Reclamo
from gestor_reclamos import GestorReclamos
from base_de_datos import engine, Base
import modelos

Base.metadata.create_all(bind=engine)

def main():
    gu= GestorUsuarios()

    u= gu.registrar_usuario(
        nombre= "Celina",
        apellido= "Houriet",
        email= "celina@houriet.com",
        username= "celihour",
        contraseña= "lacontra",
        contraseña_repetida= "lacontra",
        rol= "usuario_final"
    )

    from clasificador_externo.modules.create_csv import crear_csv
    from clasificador_externo.modules.classifier import ClaimsClassifier
    datos= crear_csv("src/clasificador_externo/data/frases.json")
    clf_global= ClaimsClassifier().fit(datos["reclamo"], datos["etiquetas"]) # type: ignore

    gr= GestorReclamos(clf_global) # type: ignore

    dept= Departamento(1, "Soporte TI")
    r= Reclamo(1, "No anda el wifi", datetime.now(), "pendiente", dept, [])
    print("Etiqueta:", r.clasificar())

if __name__ == "__main__":
    main()


