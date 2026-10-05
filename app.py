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
from forms.categoria_form import CategoriaForm


app = Flask(__name__)

app.config["SECRET_KEY"] = "clave-secreta-ferreteria"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Debe iniciar sesión para acceder."


# =========================================================
# USUARIO PARA FLASK-LOGIN
# =========================================================

class Usuario(UserMixin):

    def __init__(self, id, nombre_usuario):
        self.id = id
        self.nombre_usuario = nombre_usuario


@login_manager.user_loader
def cargar_usuario(user_id):

    conexion = obtener_conexion()

    try:
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute(
                """
                SELECT id, nombre_usuario
                FROM usuarios
                WHERE id = %s
                """,
                (user_id,)
            )

            usuario = cursor.fetchone()

            if usuario:
                return Usuario(
                    usuario["id"],
                    usuario["nombre_usuario"]
                )

            return None

    finally:
        conexion.close()


# =========================================================
# INICIO / DASHBOARD
# =========================================================

@app.route("/")
@login_required
def index():

    conexion = obtener_conexion()

    try:
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("SELECT COUNT(*) AS total FROM productos")
            total_productos = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM categorias")
            total_categorias = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM proveedores")
            total_proveedores = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM clientes")
            total_clientes = cursor.fetchone()["total"]

        return render_template(
            "index.html",
            total_productos=total_productos,
            total_categorias=total_categorias,
            total_proveedores=total_proveedores,
            total_clientes=total_clientes
        )

    finally:
        conexion.close()


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":

        nombre_usuario = request.form.get("nombre_usuario")
        password = request.form.get("password")

        conexion = obtener_conexion()

        try:
            with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

                cursor.execute(
                    """
                    SELECT id, nombre_usuario, password
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

            flash(
                "Inicio de sesión exitoso.",
                "success"
            )

            return redirect(url_for("index"))

        flash(
            "Usuario o contraseña incorrectos.",
            "danger"
        )

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Sesión cerrada correctamente.",
        "success"
    )

    return redirect(url_for("login"))


# =========================================================
# CATEGORÍAS
# =========================================================

@app.route("/categorias")
@login_required
def categorias():

    conexion = obtener_conexion()

    try:
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute(
                """
                SELECT
                    c.id,
                    c.nombre,
                    COUNT(p.id) AS total_productos
                FROM categorias c
                LEFT JOIN productos p
                    ON p.categoria_id = c.id
                GROUP BY c.id, c.nombre
                ORDER BY c.id
                """
            )

            categorias_lista = cursor.fetchall()

        return render_template(
            "categorias.html",
            categorias=categorias_lista
        )

    finally:
        conexion.close()


@app.route("/categorias/nueva", methods=["GET", "POST"])
@login_required
def nueva_categoria():

    form = CategoriaForm()

    if form.validate_on_submit():

        conexion = obtener_conexion()

        try:
            with conexion.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO categorias (nombre)
                    VALUES (%s)
                    """,
                    (form.nombre.data.strip(),)
                )

            conexion.commit()

            flash(
                "Categoría creada correctamente.",
                "success"
            )

            return redirect(url_for("categorias"))

        except Exception as error:

            conexion.rollback()

            if "duplicate key" in str(error).lower():
                flash(
                    "La categoría ya existe.",
                    "danger"
                )
            else:
                flash(
                    "No se pudo crear la categoría.",
                    "danger"
                )

        finally:
            conexion.close()

    return render_template(
        "categoria_form.html",
        form=form,
        titulo="Nueva categoría"
    )


@app.route("/categorias/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_categoria(id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute(
                """
                SELECT id, nombre
                FROM categorias
                WHERE id = %s
                """,
                (id,)
            )

            categoria = cursor.fetchone()

        if not categoria:

            flash(
                "Categoría no encontrada.",
                "danger"
            )

            return redirect(url_for("categorias"))

        form = CategoriaForm()

        if request.method == "GET":

            form.nombre.data = categoria["nombre"]

        if form.validate_on_submit():

            try:

                with conexion.cursor() as cursor:

                    cursor.execute(
                        """
                        UPDATE categorias
                        SET nombre = %s
                        WHERE id = %s
                        """,
                        (
                            form.nombre.data.strip(),
                            id
                        )
                    )

                conexion.commit()

                flash(
                    "Categoría actualizada correctamente.",
                    "success"
                )

                return redirect(url_for("categorias"))

            except Exception as error:

                conexion.rollback()

                if "duplicate key" in str(error).lower():
                    flash(
                        "Ya existe una categoría con ese nombre.",
                        "danger"
                    )
                else:
                    flash(
                        "No se pudo actualizar la categoría.",
                        "danger"
                    )

        return render_template(
            "categoria_form.html",
            form=form,
            titulo="Editar categoría"
        )

    finally:
        conexion.close()


@app.route("/categorias/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_categoria(id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM categorias
                WHERE id = %s
                """,
                (id,)
            )

        conexion.commit()

        flash(
            "Categoría eliminada correctamente.",
            "success"
        )

    except Exception:

        conexion.rollback()

        flash(
            "No se puede eliminar la categoría porque está relacionada con productos.",
            "danger"
        )

    finally:
        conexion.close()

    return redirect(url_for("categorias"))


# =========================================================
# PRODUCTOS
# =========================================================

def cargar_opciones_producto(form):

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute(
                """
                SELECT id, nombre
                FROM categorias
                ORDER BY nombre
                """
            )

            categorias_lista = cursor.fetchall()

            cursor.execute(
                """
                SELECT id, nombre, empresa
                FROM proveedores
                ORDER BY nombre
                """
            )

            proveedores_lista = cursor.fetchall()

        form.categoria_id.choices = [
            (
                categoria["id"],
                categoria["nombre"]
            )
            for categoria in categorias_lista
        ]

        form.proveedor_id.choices = [
            (
                proveedor["id"],
                f'{proveedor["nombre"]} - {proveedor["empresa"]}'
            )
            for proveedor in proveedores_lista
        ]

    finally:
        conexion.close()


@app.route("/productos")
@login_required
def productos():

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.nombre,
                    p.precio,
                    p.stock,
                    c.nombre AS categoria,
                    pr.nombre AS proveedor,
                    pr.empresa
                FROM productos p
                INNER JOIN categorias c
                    ON c.id = p.categoria_id
                INNER JOIN proveedores pr
                    ON pr.id = p.proveedor_id
                ORDER BY p.id
                """
            )

            productos_lista = cursor.fetchall()

        return render_template(
            "productos.html",
            productos=productos_lista
        )

    finally:
        conexion.close()


@app.route("/productos/nuevo", methods=["GET", "POST"])
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
                "Producto creado correctamente.",
                "success"
            )

            return redirect(url_for("productos"))

        except Exception:

            conexion.rollback()

            flash(
                "No se pudo crear el producto.",
                "danger"
            )

        finally:
            conexion.close()

    return render_template(
        "producto_form.html",
        form=form,
        titulo="Nuevo producto"
    )


@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_producto(id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

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

        if not producto:

            flash(
                "Producto no encontrado.",
                "danger"
            )

            return redirect(url_for("productos"))

        form = ProductoForm()

        cargar_opciones_producto(form)

        if request.method == "GET":

            form.nombre.data = producto["nombre"]
            form.categoria_id.data = producto["categoria_id"]
            form.proveedor_id.data = producto["proveedor_id"]
            form.precio.data = producto["precio"]
            form.stock.data = producto["stock"]

        if form.validate_on_submit():

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

                return redirect(url_for("productos"))

            except Exception:

                conexion.rollback()

                flash(
                    "No se pudo actualizar el producto.",
                    "danger"
                )

        return render_template(
            "producto_form.html",
            form=form,
            titulo="Editar producto"
        )

    finally:
        conexion.close()


@app.route("/productos/eliminar/<int:id>", methods=["POST"])
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

    except Exception:

        conexion.rollback()

        flash(
            "No se pudo eliminar el producto.",
            "danger"
        )

    finally:
        conexion.close()

    return redirect(url_for("productos"))


# =========================================================
# PROVEEDORES
# =========================================================

@app.route("/proveedores")
@login_required
def proveedores():

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute(
                """
                SELECT
                    pr.id,
                    pr.nombre,
                    pr.empresa,
                    pr.ciudad,
                    pr.telefono,
                    pr.estado,
                    COUNT(p.id) AS total_productos
                FROM proveedores pr
                LEFT JOIN productos p
                    ON p.proveedor_id = pr.id
                GROUP BY
                    pr.id,
                    pr.nombre,
                    pr.empresa,
                    pr.ciudad,
                    pr.telefono,
                    pr.estado
                ORDER BY pr.id
                """
            )

            proveedores_lista = cursor.fetchall()

        return render_template(
            "proveedores.html",
            proveedores=proveedores_lista
        )

    finally:
        conexion.close()


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
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
                        form.estado.data
                    )
                )

            conexion.commit()

            flash(
                "Proveedor creado correctamente.",
                "success"
            )

            return redirect(url_for("proveedores"))

        except Exception:

            conexion.rollback()

            flash(
                "No se pudo crear el proveedor.",
                "danger"
            )

        finally:
            conexion.close()

    return render_template(
        "proveedor_form.html",
        form=form,
        titulo="Nuevo proveedor"
    )


@app.route("/proveedores/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_proveedor(id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

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

        if not proveedor:

            flash(
                "Proveedor no encontrado.",
                "danger"
            )

            return redirect(url_for("proveedores"))

        form = ProveedorForm()

        if request.method == "GET":

            form.nombre.data = proveedor["nombre"]
            form.empresa.data = proveedor["empresa"]
            form.ciudad.data = proveedor["ciudad"]
            form.telefono.data = proveedor["telefono"]
            form.estado.data = proveedor["estado"]

        if form.validate_on_submit():

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
                            form.estado.data,
                            id
                        )
                    )

                conexion.commit()

                flash(
                    "Proveedor actualizado correctamente.",
                    "success"
                )

                return redirect(url_for("proveedores"))

            except Exception:

                conexion.rollback()

                flash(
                    "No se pudo actualizar el proveedor.",
                    "danger"
                )

        return render_template(
            "proveedor_form.html",
            form=form,
            titulo="Editar proveedor"
        )

    finally:
        conexion.close()


@app.route("/proveedores/eliminar/<int:id>", methods=["POST"])
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

    except Exception:

        conexion.rollback()

        flash(
            "No se puede eliminar el proveedor porque está relacionado con productos.",
            "danger"
        )

    finally:
        conexion.close()

    return redirect(url_for("proveedores"))


# =========================================================
# CLIENTES
# =========================================================

@app.route("/clientes")
@login_required
def clientes():

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    nombre,
                    empresa,
                    ciudad,
                    estado
                FROM clientes
                ORDER BY id
                """
            )

            clientes_lista = cursor.fetchall()

        return render_template(
            "clientes.html",
            clientes=clientes_lista
        )

    finally:
        conexion.close()


@app.route("/clientes/nuevo", methods=["GET", "POST"])
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
                        form.estado.data
                    )
                )

            conexion.commit()

            flash(
                "Cliente creado correctamente.",
                "success"
            )

            return redirect(url_for("clientes"))

        except Exception:

            conexion.rollback()

            flash(
                "No se pudo crear el cliente.",
                "danger"
            )

        finally:
            conexion.close()

    return render_template(
        "cliente_form.html",
        form=form,
        titulo="Nuevo cliente"
    )


@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_cliente(id):

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

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

        if not cliente:

            flash(
                "Cliente no encontrado.",
                "danger"
            )

            return redirect(url_for("clientes"))

        form = ClienteForm()

        if request.method == "GET":

            form.nombre.data = cliente["nombre"]
            form.empresa.data = cliente["empresa"]
            form.ciudad.data = cliente["ciudad"]
            form.estado.data = cliente["estado"]

        if form.validate_on_submit():

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
                            form.estado.data,
                            id
                        )
                    )

                conexion.commit()

                flash(
                    "Cliente actualizado correctamente.",
                    "success"
                )

                return redirect(url_for("clientes"))

            except Exception:

                conexion.rollback()

                flash(
                    "No se pudo actualizar el cliente.",
                    "danger"
                )

        return render_template(
            "cliente_form.html",
            form=form,
            titulo="Editar cliente"
        )

    finally:
        conexion.close()


@app.route("/clientes/eliminar/<int:id>", methods=["POST"])
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

    except Exception:

        conexion.rollback()

        flash(
            "No se pudo eliminar el cliente.",
            "danger"
        )

    finally:
        conexion.close()

    return redirect(url_for("clientes"))


# =========================================================
# EJECUTAR APLICACIÓN
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)