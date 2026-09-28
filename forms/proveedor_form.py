from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class ProveedorForm(FlaskForm):

    nombre = StringField(
        "Nombre del contacto",
        validators=[
            DataRequired(),
            Length(min=3, max=100)
        ]
    )

    empresa = StringField(
        "Empresa",
        validators=[
            DataRequired(),
            Length(min=2, max=100)
        ]
    )

    ciudad = StringField(
        "Ciudad",
        validators=[
            DataRequired(),
            Length(min=2, max=50)
        ]
    )

    telefono = StringField(
        "Teléfono",
        validators=[
            DataRequired(),
            Length(min=7, max=20)
        ]
    )

    estado = SelectField(
        "Estado",
        choices=[
            ("Activo", "Activo"),
            ("Pendiente", "Pendiente")
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField("Guardar proveedor")