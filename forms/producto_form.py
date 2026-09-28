from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class ProductoForm(FlaskForm):

    nombre = StringField(
        "Nombre",
        validators=[DataRequired(message="El nombre es obligatorio.")]
    )

    categoria_id = SelectField(
        "Categoría",
        coerce=int,
        validators=[DataRequired(message="Seleccione una categoría.")]
    )

    proveedor_id = SelectField(
        "Proveedor",
        coerce=int,
        validators=[DataRequired(message="Seleccione un proveedor.")]
    )

    precio = DecimalField(
        "Precio",
        places=2,
        validators=[
            DataRequired(message="El precio es obligatorio."),
            NumberRange(min=0, message="El precio no puede ser negativo.")
        ]
    )

    stock = IntegerField(
        "Stock",
        validators=[
            DataRequired(message="El stock es obligatorio."),
            NumberRange(min=0, message="El stock no puede ser negativo.")
        ]
    )

    submit = SubmitField("Guardar")