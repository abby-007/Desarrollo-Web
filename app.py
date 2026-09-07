from flask import Flask, render_template, redirect, url_for, flash
import sqlite3
from pathlib import Path
from forms.producto_form import ProductoForm

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
    return render_template("clientes.html")


@app.route("/proveedores")
def proveedores():
    return render_template("proveedores.html")


@app.route("/facturacion")
def facturacion():
    return render_template("facturacion.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)