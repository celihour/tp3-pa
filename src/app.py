import os
import sys
from flask import (Flask, render_template, request, redirect, url_for, session, flash, Response)
from werkzeug.utils import secure_filename

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

PROJECT_ROOT = os.path.dirname(THIS_DIR)
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from gestor_usuario import GestorUsuarios
from gestor_reclamos import GestorReclamos
from gestor_bdd import GestorBaseDatos

app = Flask(__name__)
app.secret_key = "TU_SECRETO_AQUI"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

gu = GestorUsuarios()
gr = GestorReclamos()
gbd= GestorBaseDatos()

@app.route("/", methods=["GET"])
def index():
    if session.get("username"):
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    usuario = gu.login(
        username=request.form.get("username"), # type: ignore
        contraseña=request.form.get("password") # type: ignore
    )
    if usuario:
        session["user_id"]  = usuario.id_usuario
        session["username"] = usuario.username
        session["rol"]      = usuario.rol
        flash("Login exitoso", "success")
        if usuario.rol == "jefe_departamento":
                session["departamento_id"]     = usuario.departamento.id # type: ignore
                session["departamento_nombre"] = usuario.departamento.nombre # type: ignore
        return redirect(url_for("home"))
    flash("Usuario o contraseña incorrectos", "danger")
    return redirect(url_for("index"))

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        try:
            usuario = gu.registrar_usuario(
                nombre=request.form.get("nombre"), # type: ignore
                apellido=request.form.get("apellido"), # type: ignore
                email=request.form.get("email"), # type: ignore
                username=request.form.get("username"), # type: ignore
                contraseña=request.form.get("password"), # type: ignore
                contraseña_repetida=request.form.get("password2"), # type: ignore
                rol="usuario_final"
            )
            
        except ValueError as e:
            flash(str(e), "danger")
    return render_template("registro.html")

@app.route("/home")
def home():
    if not session.get("username"):
        return redirect(url_for("index"))
    return render_template("home.html", username=session.get("username"), rol=session.get("rol"))

@app.route("/reclamo/nuevo", methods=["GET", "POST"]) # type: ignore
def nuevo_reclamo():
    if not session.get("username"):
        return redirect(url_for("index"))
    if request.method == "POST":
        usuario = gu.obtener_por_username(session["username"]) # type: ignore
        foto = request.files.get("foto")
        foto_path = None
        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            foto_path = filename
        reclamo = gr.crear_adherir(usuario=usuario, contenido=request.form.get("contenido"), nombre_departamento=request.form.get("departamento"), foto_path=foto_path) # type: ignore
        flash(f"Reclamo #{reclamo.id_reclamo} procesado", "success")
        return redirect(url_for("listar_reclamos"))
    return render_template("nuevo_reclamo.html")

# Listar reclamos pendientes
@app.route("/reclamos", methods=["GET"])
def listar_reclamos():
    if not session.get("username"):
        return redirect(url_for("index"))
    depto = request.args.get("departamento")
    reclamos = gr.listar_pendientes(depto)
    return render_template("listar_reclamos.html", reclamos=reclamos)

@app.route("/dashboard_departamento", methods=["GET"])
def dashboard_departamento():
    # Si no está logueado o no es jefe, lo expulsamos
    if session.get("rol") != "jefe_departamento":
        flash("Acceso no autorizado", "danger")
        return redirect(url_for("index"))

    depto_nombre = session["departamento_nombre"]
    estadisticas = gr.estadisticas_por_departamento(depto_nombre)
    pendientes   = gr.listar_pendientes(depto_nombre)
    top_pal  = gr.top_palabras(limit=15, departamento_id=session["departamento_id"]) # type: ignore
    

    return render_template(
        "dashboard_departamento.html",
        depto=depto_nombre,
        estadisticas=estadisticas,
        top_pal=top_pal,
        reclamos_pendientes=pendientes
    )

@app.route("/dashboard_departamento/manejar", methods=["POST"])
def manejar_reclamo():
    # Sólo jefes de departamento
    if session.get("rol") != "jefe_departamento":
        flash("Acceso no autorizado", "danger")
        return redirect(url_for("index"))

    depto_nombre = session["departamento_nombre"]
    reclamo_id   = int(request.form["reclamo_id"])
    nuevo_estado = request.form["nuevo_estado"]

    r = gr.obtener_reclamo_por_id(reclamo_id)
    if r.departamento.nombre != depto_nombre: # type: ignore
        flash("No puedes manejar reclamos de otro departamento", "danger")
        return redirect(url_for("dashboard_departamento"))

    if gr.cambiar_estado(reclamo_id, nuevo_estado):
        flash("Estado actualizado", "success")
    else:
        flash("Error al actualizar", "danger")

    return redirect(url_for("dashboard_departamento"))

@app.route("/dashboard_tecnico")
def dashboard_tecnico():
    if session.get("rol") != "secretario_tecnico":
        flash("Acceso no autorizado", "danger")
        return redirect(url_for("index"))

    # Obtener datos
    stats    = gr.estadisticas()
    top_pal  = gr.top_palabras(limit=15)
    pendientes = gr.listar_pendientes()

    # Lista de departamentos para el select
    departamentos = gr.listar_departamentos()  # Necesitamos este método

    
    return render_template(
        "dashboard_tecnico.html",
        estadisticas=stats,
        top_pal=top_pal,
        reclamos_pendientes=pendientes,
        departamentos=departamentos
    )

@app.route("/dashboard/<int:dept_id>/reporte.html")
def reporte_departamento(dept_id):
    # 1) Datos
    depto = gr.base_de_datos.obtener_o_crear_departamento(dept_id)  # tu método
    stats = gr.base_de_datos.estadisticas_por_estado(departamento_id=dept_id)
    reclamos = gr.listar_pendientes(depto.nombre) # type: ignore

    # 2) Render a string
    html = render_template(
        "reporte_departamento.html",
        depto=depto,
        estadisticas=stats,
        reclamos=reclamos
    )

    # 3) Devolver como descarga
    filename = f"reporte_{depto.nombre.replace(' ','_')}.html"
    return Response(
        html,
        mimetype="text/html",
        headers={
          "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@app.route("/dashboard/tecnico/reporte.html")
def reporte_tecnico():
    stats = gr.base_de_datos.estadisticas_por_estado()
    reclamos = gr.listar_pendientes()  # todos
    html = render_template(
        "reporte_departamento.html",   # reutilizamos la misma plantilla
        depto=type("D", (), {"nombre":"Global"})(),
        estadisticas=stats,
        reclamos=reclamos
    )
    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition":"attachment; filename=reporte_global.html"}
    )


@app.route("/dashboard_tecnico/derivar", methods=["POST"])
def derivar_reclamo():
    # Sólo secretario técnico
    if session.get("rol") != "secretario_tecnico":
        flash("Acceso no autorizado", "danger")
        return redirect(url_for("index"))

    reclamo_id          = int(request.form.get("reclamo_id")) # type: ignore
    depto_destino       = request.form.get("departamento_destino")

    success = gr.derivar_reclamo(reclamo_id, depto_destino) # type: ignore
    if success:
        flash(f"Reclamo #{reclamo_id} derivado a {depto_destino}", "success")
    else:
        flash("Error al derivar el reclamo", "danger")

    return redirect(url_for("dashboard_tecnico"))

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/mis_reclamos")
def mis_reclamos():
    if not session.get("user_id"):
        return redirect(url_for("index"))
    usuario = gu.obtener_por_id(session["user_id"])
    reclamos = gr.mis_reclamos(usuario) # type: ignore
    return render_template("mis_reclamos.html", reclamos=reclamos)

@app.route("/ayuda")
def ayuda():
    rol = session.get("rol")
    # Solo roles administrativos pueden ver ayuda de dashboards
    if rol not in ("jefe_departamento", "secretario_tecnico"):
        flash("Acceso no autorizado", "danger")
        return redirect(url_for("index"))
    return render_template("ayuda.html", rol=rol)

@app.route("/dashboard/<int:dept_id>/analitica")
def analitica_departamento(dept_id):
    # 1) Obtiene el conteo por estado
    stats = gbd.estadisticas_por_estado(departamento_id=dept_id)
    # 2) Genera la imagen PNG en Base64
    pie_png = gbd.generar_pie(stats)
    # 3) Rinde la plantilla pasando pie_png
    return render_template("analitica_depto.html",
                           estadisticas=stats,
                           pie_png=pie_png,
                           dept_id=dept_id)

@app.route("/dashboard/tecnico/analitica")
def analitica_tecnico():
    stats = gbd.estadisticas_por_estado()  # sin filtro
    pie_png = gbd.generar_pie(stats)
    return render_template("analitica_tecnico.html",
                           estadisticas=stats,
                           pie_png=pie_png)

@app.errorhandler(404)
def pagina_no_encontrada(error):
    # Renderiza templates/404.html
    return render_template("404.html"), 404

@app.errorhandler(500)
def error_interno(error):
    # Renderiza templates/500.html
    return render_template("500.html"), 500
