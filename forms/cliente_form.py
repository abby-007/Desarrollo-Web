from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class ClienteForm(FlaskForm):

    nombre = StringField(
        "Nombre del cliente",
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

    estado = SelectField(
        "Estado",
        choices=[
            ("Activo", "Activo"),
            ("Pendiente", "Pendiente")
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField("Guardar cliente")