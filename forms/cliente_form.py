from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class ClienteForm(FlaskForm):

    nombre = StringField(
        "Nombre del cliente",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(
                min=3,
                max=100,
                message="El nombre debe tener entre 3 y 100 caracteres."
            )
        ]
    )

    empresa = StringField(
        "Empresa",
        validators=[
            DataRequired(message="La empresa es obligatoria."),
            Length(
                min=2,
                max=100,
                message="La empresa debe tener entre 2 y 100 caracteres."
            )
        ]
    )

    ciudad = StringField(
        "Ciudad",
        validators=[
            DataRequired(message="La ciudad es obligatoria."),
            Length(
                min=2,
                max=50,
                message="La ciudad debe tener entre 2 y 50 caracteres."
            )
        ]
    )

    estado = SelectField(
        "Estado",
        choices=[
            ("Activo", "Activo"),
            ("Pendiente", "Pendiente")
        ],
        validators=[
            DataRequired(message="El estado es obligatorio.")
        ]
    )

    submit = SubmitField("Guardar cliente")