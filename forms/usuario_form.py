from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class UsuarioForm(FlaskForm):

    nombre_usuario = StringField(
        "Nombre de usuario",
        validators=[
            DataRequired(),
            Length(min=3, max=100)
        ]
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(),
            Length(min=4, max=100)
        ]
    )

    submit = SubmitField("Continuar")