from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import check_password_hash

from psycopg2.extras import RealDictCursor

from conexion.conexion import obtener_conexion

from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm


app = Flask(__name__)

app.config["SECRET_KEY"] = "clave-secreta-desarrollo"


# ==========================================================
# FLASK LOGIN
# ==========================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


class Usuario(UserMixin):

    def __init__(self, id, nombre_usuario):
        self.id = str(id)
        self.nombre_usuario = nombre_usuario


@login_manager.user_loader
def cargar_usuario(user_id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                """
                SELECT id, nombre_usuario
                FROM usuarios
                WHERE id = %s
                """,
                (user_id,)
            )

            usuario = cursor.fetchone()

    finally:

        conexion.close()

    if usuario:

        return Usuario(
            usuario["id"],
            usuario["nombre_usuario"]
        )

    return None


# ==========================================================
# INICIO
# ==========================================================

@app.route("/")
@login_required
def index():

    return render_template("index.html")


# ==========================================================
# LOGIN
# ==========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for("index")
        )

    if request.method == "POST":

        nombre_usuario = request.form.get(
            "nombre_usuario",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        conexion = obtener_conexion()

        try:

            with conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        nombre_usuario,
                        password
                    FROM usuarios
                    WHERE nombre_usuario = %s
                    """,
                    (nombre_usuario,)
                )

                usuario = cursor.fetchone()

        finally:

            conexion.close()

        if usuario and check_password_hash(
            usuario["password"],
            password
        ):

            usuario_login = Usuario(
                usuario["id"],
                usuario["nombre_usuario"]
            )

            login_user(usuario_login)

            siguiente = request.args.get("next")

            if siguiente and siguiente.startswith("/"):
                return redirect(siguiente)

            return redirect(
                url_for("index")
            )

        flash(
            "Usuario o contraseña incorrectos.",
            "danger"
        )

    return render_template(
        "login.html"
    )


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Sesión cerrada correctamente.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ==========================================================
# PRODUCTOS - SELECT + JOIN
# ==========================================================

@app.route("/productos")
@login_required
def productos():

    conexion = obtener_conexion()

    try:

        with conexion.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.nombre,
                    c.nombre AS categoria,
                    pr.empresa AS proveedor,
                    p.precio,
                    p.stock
                FROM productos p
                INNER JOIN categorias c
                    ON p.categoria_id = c.id
                INNER JOIN proveedores pr
                    ON p.proveedor_id = pr.id
                ORDER BY p.id DESC
                """
            )

            productos = cursor.fetchall()

    finally:

        conexion.close()

    return render_template(
        "productos.html",
        productos=productos
    )


# ==========================================================
# PRODUCTOS - NUEVO
# ==========================================================

@app.route(
    "/productos/nuevo",
    methods=["GET", "POST"]
)
@login_required
def nuevo_producto():

    form = ProductoForm()

    cargar_opciones_producto(form)

    if form.validate_on_submit():

        conexion = obtener_conexion()

        try:

            with conexion.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO productos
                    (
                        nombre,
                        categoria_id,
                        proveedor_id,
                        precio,
                        stock
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        form.nombre.data.strip(),
                        form.categoria_id.data,
                        form.proveedor_id.data,
                        form.precio.data,
                        form.stock.data
                    )
                )

            conexion.commit()

            flash(
                "Producto agregado correctamente.",
                "success"
            )

            return redirect(
                url_for("productos")
            )

        except Exception as e:

            conexion.rollback()

            flash(
                f"Error al agregar producto: {e}",
                "danger"
            )

        finally:

            conexion.close()

    return render_template(
        "producto_form.html",
        form=form,
        titulo="Nuevo producto"
    )


# ==========================================================
# PRODUCTOS - EDITAR
# ==========================================================

@app.route(
    "/productos/editar/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def editar_producto(id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    nombre,
                    categoria_id,
                    proveedor_id,
                    precio,
                    stock
                FROM productos
                WHERE id = %s
                """,
                (id,)
            )

            producto = cursor.fetchone()

    finally:

        conexion.close()

    if not producto:

        flash(
            "Producto no encontrado.",
            "danger"
        )

        return redirect(
            url_for("productos")
        )

    form = ProductoForm()

    cargar_opciones_producto(form)

    if request.method == "GET":

        form.nombre.data = producto["nombre"]
        form.categoria_id.data = producto["categoria_id"]
        form.proveedor_id.data = producto["proveedor_id"]
        form.precio.data = producto["precio"]
        form.stock.data = producto["stock"]

    if form.validate_on_submit():

        conexion = obtener_conexion()

        try:

            with conexion.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE productos
                    SET
                        nombre = %s,
                        categoria_id = %s,
                        proveedor_id = %s,
                        precio = %s,
                        stock = %s
                    WHERE id = %s
                    """,
                    (
                        form.nombre.data.strip(),
                        form.categoria_id.data,
                        form.proveedor_id.data,
                        form.precio.data,
                        form.stock.data,
                        id
                    )
                )

            conexion.commit()

            flash(
                "Producto actualizado correctamente.",
                "success"
            )

            return redirect(
                url_for("productos")
            )

        except Exception as e:

            conexion.rollback()

            flash(
                f"Error al actualizar producto: {e}",
                "danger"
            )

        finally:

            conexion.close()

    return render_template(
        "producto_form.html",
        form=form,
        titulo="Editar producto"
    )


# ==========================================================
# PRODUCTOS - ELIMINAR
# ==========================================================

@app.route(
    "/productos/eliminar/<int:id>",
    methods=["POST"]
)
@login_required
def eliminar_producto(id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM productos
                WHERE id = %s
                """,
                (id,)
            )

        conexion.commit()

        flash(
            "Producto eliminado correctamente.",
            "success"
        )

    except Exception as e:

        conexion.rollback()

        flash(
            f"No se pudo eliminar el producto: {e}",
            "danger"
        )

    finally:

        conexion.close()

    return redirect(
        url_for("productos")
    )


# ==========================================================
# CARGAR OPCIONES DE PRODUCTOS
# ==========================================================

def cargar_opciones_producto(form):

    conexion = obtener_conexion()

    try:

        with conexion.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                """
                SELECT id, nombre
                FROM categorias
                ORDER BY nombre
                """
            )

            categorias = cursor.fetchall()

            cursor.execute(
                """
                SELECT id, empresa
                FROM proveedores
                ORDER BY empresa
                """
            )

            proveedores = cursor.fetchall()

    finally:

        conexion.close()

    form.categoria_id.choices = [
        (
            categoria["id"],
            categoria["nombre"]
        )
        for categoria in categorias
    ]

    form.proveedor_id.choices = [
        (
            proveedor["id"],
            proveedor["empresa"]
        )
        for proveedor in proveedores
    ]


# ==========================================================
# PROVEEDORES
# ==========================================================

@app.route("/proveedores")
@login_required
def proveedores():

    conexion = obtener_conexion()

    try:

        with conexion.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    nombre,
                    empresa,
                    ciudad,
                    telefono,
                    estado
                FROM proveedores
                ORDER BY id DESC
                """
            )

            proveedores = cursor.fetchall()

    finally:

        conexion.close()

    return render_template(
        "proveedores.html",
        proveedores=proveedores
    )


# ==========================================================
# PROVEEDOR - NUEVO
# ==========================================================

@app.route(
    "/proveedores/nuevo",
    methods=["GET", "POST"]
)
@login_required
def nuevo_proveedor():

    form = ProveedorForm()

    if form.validate_on_submit():

        conexion = obtener_conexion()

        try:

            with conexion.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO proveedores
                    (
                        nombre,
                        empresa,
                        ciudad,
                        telefono,
                        estado
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        form.nombre.data.strip(),
                        form.empresa.data.strip(),
                        form.ciudad.data.strip(),
                        form.telefono.data.strip(),
                        form.estado.data.strip()
                    )
                )

            conexion.commit()

            flash(
                "Proveedor agregado correctamente.",
                "success"
            )

            return redirect(
                url_for("proveedores")
            )

        except Exception as e:

            conexion.rollback()

            flash(
                f"Error al agregar proveedor: {e}",
                "danger"
            )

        finally:

            conexion.close()

    return render_template(
        "proveedor_form.html",
        form=form,
        titulo="Nuevo proveedor"
    )


# ==========================================================
# PROVEEDORES - EDITAR
# ==========================================================

@app.route(
    "/proveedores/editar/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def editar_proveedor(id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    nombre,
                    empresa,
                    ciudad,
                    telefono,
                    estado
                FROM proveedores
                WHERE id = %s
                """,
                (id,)
            )

            proveedor = cursor.fetchone()

    finally:

        conexion.close()

    if not proveedor:

        flash(
            "Proveedor no encontrado.",
            "danger"
        )

        return redirect(
            url_for("proveedores")
        )

    form = ProveedorForm()

    if request.method == "GET":

        form.nombre.data = proveedor["nombre"]
        form.empresa.data = proveedor["empresa"]
        form.ciudad.data = proveedor["ciudad"]
        form.telefono.data = proveedor["telefono"]
        form.estado.data = proveedor["estado"]

    if form.validate_on_submit():

        conexion = obtener_conexion()

        try:

            with conexion.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE proveedores
                    SET
                        nombre = %s,
                        empresa = %s,
                        ciudad = %s,
                        telefono = %s,
                        estado = %s
                    WHERE id = %s
                    """,
                    (
                        form.nombre.data.strip(),
                        form.empresa.data.strip(),
                        form.ciudad.data.strip(),
                        form.telefono.data.strip(),
                        form.estado.data.strip(),
                        id
                    )
                )

            conexion.commit()

            flash(
                "Proveedor actualizado correctamente.",
                "success"
            )

            return redirect(
                url_for("proveedores")
            )

        except Exception as e:

            conexion.rollback()

            flash(
                f"Error al actualizar proveedor: {e}",
                "danger"
            )

        finally:

            conexion.close()

    return render_template(
        "proveedor_form.html",
        form=form,
        titulo="Editar proveedor"
    )


# ==========================================================
# PROVEEDORES - ELIMINAR
# ==========================================================

@app.route(
    "/proveedores/eliminar/<int:id>",
    methods=["POST"]
)
@login_required
def eliminar_proveedor(id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM proveedores
                WHERE id = %s
                """,
                (id,)
            )

        conexion.commit()

        flash(
            "Proveedor eliminado correctamente.",
            "success"
        )

    except Exception as e:

        conexion.rollback()

        flash(
            f"No se pudo eliminar el proveedor: {e}",
            "danger"
        )

    finally:

        conexion.close()

    return redirect(
        url_for("proveedores")
    )


# ==========================================================
# CLIENTES
# ==========================================================

@app.route("/clientes")
@login_required
def clientes():

    conexion = obtener_conexion()

    try:

        with conexion.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    nombre,
                    empresa,
                    ciudad,
                    estado
                FROM clientes
                ORDER BY id DESC
                """
            )

            clientes = cursor.fetchall()

    finally:

        conexion.close()

    return render_template(
        "clientes.html",
        clientes=clientes
    )


# ==========================================================
# CLIENTE - NUEVO
# ==========================================================

@app.route(
    "/clientes/nuevo",
    methods=["GET", "POST"]
)
@login_required
def nuevo_cliente():

    form = ClienteForm()

    if form.validate_on_submit():

        conexion = obtener_conexion()

        try:

            with conexion.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO clientes
                    (
                        nombre,
                        empresa,
                        ciudad,
                        estado
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        form.nombre.data.strip(),
                        form.empresa.data.strip(),
                        form.ciudad.data.strip(),
                        form.estado.data.strip()
                    )
                )

            conexion.commit()

            flash(
                "Cliente agregado correctamente.",
                "success"
            )

            return redirect(
                url_for("clientes")
            )

        except Exception as e:

            conexion.rollback()

            flash(
                f"Error al agregar cliente: {e}",
                "danger"
            )

        finally:

            conexion.close()

    return render_template(
        "cliente_form.html",
        form=form,
        titulo="Nuevo cliente"
    )


# ==========================================================
# CLIENTES - EDITAR
# ==========================================================

@app.route(
    "/clientes/editar/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def editar_cliente(id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    nombre,
                    empresa,
                    ciudad,
                    estado
                FROM clientes
                WHERE id = %s
                """,
                (id,)
            )

            cliente = cursor.fetchone()

    finally:

        conexion.close()

    if not cliente:

        flash(
            "Cliente no encontrado.",
            "danger"
        )

        return redirect(
            url_for("clientes")
        )

    form = ClienteForm()

    if request.method == "GET":

        form.nombre.data = cliente["nombre"]
        form.empresa.data = cliente["empresa"]
        form.ciudad.data = cliente["ciudad"]
        form.estado.data = cliente["estado"]

    if form.validate_on_submit():

        conexion = obtener_conexion()

        try:

            with conexion.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE clientes
                    SET
                        nombre = %s,
                        empresa = %s,
                        ciudad = %s,
                        estado = %s
                    WHERE id = %s
                    """,
                    (
                        form.nombre.data.strip(),
                        form.empresa.data.strip(),
                        form.ciudad.data.strip(),
                        form.estado.data.strip(),
                        id
                    )
                )

            conexion.commit()

            flash(
                "Cliente actualizado correctamente.",
                "success"
            )

            return redirect(
                url_for("clientes")
            )

        except Exception as e:

            conexion.rollback()

            flash(
                f"Error al actualizar cliente: {e}",
                "danger"
            )

        finally:

            conexion.close()

    return render_template(
        "cliente_form.html",
        form=form,
        titulo="Editar cliente"
    )


# ==========================================================
# CLIENTES - ELIMINAR
# ==========================================================

@app.route(
    "/clientes/eliminar/<int:id>",
    methods=["POST"]
)
@login_required
def eliminar_cliente(id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM clientes
                WHERE id = %s
                """,
                (id,)
            )

        conexion.commit()

        flash(
            "Cliente eliminado correctamente.",
            "success"
        )

    except Exception as e:

        conexion.rollback()

        flash(
            f"No se pudo eliminar el cliente: {e}",
            "danger"
        )

    finally:

        conexion.close()

    return redirect(
        url_for("clientes")
    )


# ==========================================================
# EJECUTAR APLICACIÓN
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )