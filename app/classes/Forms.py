from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError

#Function to validate a person's name. This creates a custom validator.
def validate_name(form, field):
    if len(field.data) > 12:
        raise ValidationError('Name must be less than 12 characters long.')

#Class to generate the login form for the main page
class LoginForm(FlaskForm):
    room_code = StringField('Room Code', validators=[DataRequired()])
    name = StringField('Name (Limit 12 Characters)', validators=[DataRequired(), validate_name])
    submit = SubmitField('Join')

