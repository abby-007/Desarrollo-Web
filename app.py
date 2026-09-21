from flask import Flask, render_template, redirect, url_for, flash
import sqlite3
from pathlib import Path
from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "clave-secreta-desarrollo"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "ferreteria.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            empresa TEXT NOT NULL,
            ciudad TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            empresa TEXT NOT NULL,
            ciudad TEXT NOT NULL,
            telefono TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/productos")
def productos():
    conn = get_db_connection()

    productos = conn.execute("""
        SELECT id, nombre, categoria, precio, stock
        FROM productos
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("productos.html", productos=productos)


@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    form = ProductoForm()

    if form.validate_on_submit():
        conn = get_db_connection()

        conn.execute("""
            INSERT INTO productos
            (nombre, categoria, precio, stock)
            VALUES (?, ?, ?, ?)
        """, (
            form.nombre.data,
            form.categoria.data,
            form.precio.data,
            form.stock.data
        ))

        conn.commit()
        conn.close()

        flash("Producto guardado correctamente.", "success")

        return redirect(url_for("productos"))

    return render_template("producto_form.html", form=form)


@app.route("/clientes")
def clientes():
    conn = get_db_connection()

    clientes = conn.execute("""
        SELECT id, nombre, empresa, ciudad, estado
        FROM clientes
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("clientes.html", clientes=clientes)


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    form = ClienteForm()

    if form.validate_on_submit():
        conn = get_db_connection()

        conn.execute("""
            INSERT INTO clientes
            (nombre, empresa, ciudad, estado)
            VALUES (?, ?, ?, ?)
        """, (
            form.nombre.data,
            form.empresa.data,
            form.ciudad.data,
            form.estado.data
        ))

        conn.commit()
        conn.close()

        flash("Cliente guardado correctamente.", "success")

        return redirect(url_for("clientes"))

    return render_template("cliente_form.html", form=form)


@app.route("/proveedores")
def proveedores():
    conn = get_db_connection()

    proveedores = conn.execute("""
        SELECT id, nombre, empresa, ciudad, telefono, estado
        FROM proveedores
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("proveedores.html", proveedores=proveedores)


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
def nuevo_proveedor():
    form = ProveedorForm()

    if form.validate_on_submit():
        conn = get_db_connection()

        conn.execute("""
            INSERT INTO proveedores
            (nombre, empresa, ciudad, telefono, estado)
            VALUES (?, ?, ?, ?, ?)
        """, (
            form.nombre.data,
            form.empresa.data,
            form.ciudad.data,
            form.telefono.data,
            form.estado.data
        ))

        conn.commit()
        conn.close()

        flash("Proveedor guardado correctamente.", "success")

        return redirect(url_for("proveedores"))

    return render_template("proveedor_form.html", form=form)


@app.route("/proveedores/editar/<int:id>", methods=["GET", "POST"])
def editar_proveedor(id):
    conn = get_db_connection()

    proveedor = conn.execute("""
        SELECT *
        FROM proveedores
        WHERE id = ?
    """, (id,)).fetchone()

    if proveedor is None:
        conn.close()
        flash("Proveedor no encontrado.", "danger")
        return redirect(url_for("proveedores"))

    form = ProveedorForm()

    if form.validate_on_submit():
        conn.execute("""
            UPDATE proveedores
            SET nombre = ?,
                empresa = ?,
                ciudad = ?,
                telefono = ?,
                estado = ?
            WHERE id = ?
        """, (
            form.nombre.data,
            form.empresa.data,
            form.ciudad.data,
            form.telefono.data,
            form.estado.data,
            id
        ))

        conn.commit()
        conn.close()

        flash("Proveedor actualizado correctamente.", "success")

        return redirect(url_for("proveedores"))

    if not form.is_submitted():
        form.nombre.data = proveedor["nombre"]
        form.empresa.data = proveedor["empresa"]
        form.ciudad.data = proveedor["ciudad"]
        form.telefono.data = proveedor["telefono"]
        form.estado.data = proveedor["estado"]

    conn.close()

    return render_template("proveedor_form.html", form=form)


@app.route("/proveedores/eliminar/<int:id>", methods=["POST"])
def eliminar_proveedor(id):
    conn = get_db_connection()

    proveedor = conn.execute("""
        SELECT id
        FROM proveedores
        WHERE id = ?
    """, (id,)).fetchone()

    if proveedor is None:
        conn.close()
        flash("Proveedor no encontrado.", "danger")
        return redirect(url_for("proveedores"))

    conn.execute("""
        DELETE FROM proveedores
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    flash("Proveedor eliminado correctamente.", "success")

    return redirect(url_for("proveedores"))


@app.route("/facturacion")
def facturacion():
    return render_template("facturacion.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)