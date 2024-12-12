from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length



class AddUserForm(FlaskForm):
    '''Provides form to add user'''

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login user form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class CreatePlaylistForm(FlaskForm):
    """ Create playlist for users """

    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    image = StringField("(Optional) Image URL")


class NewSongForPlaylistForm(FlaskForm):
    """Form for adding a song to playlist."""

    song = SelectField("Pick 'n' Playtify ", coerce=int)
