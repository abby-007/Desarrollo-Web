from flask import Flask, render_template
from forms.producto_form import ProductoForm
app = Flask(__name__)
app.config["SECRET_KEY"] = "clave-secreta-desarrollo"

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/productos")
def productos():
    return render_template("productos.html")

@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    form = ProductoForm()

    if form.validate_on_submit():
        return "Producto guardado correctamente"

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
    app.run(debug=True)