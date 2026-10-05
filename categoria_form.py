from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CategoriaForm(FlaskForm):

    nombre = StringField(
        "Nombre de la categoría",
        validators=[
            DataRequired(
                message="El nombre es obligatorio."
            ),
            Length(
                min=2,
                max=80,
                message="El nombre debe tener entre 2 y 80 caracteres."
            )
        ]
    )

    submit = SubmitField("Guardar")