from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CreateTemplateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    code = HiddenField('Code')
    body = TextAreaField('Text')
    party_labels = HiddenField('Party Labels', default="[]")
    params = TextAreaField('Parameters', default="[]")
    submit = SubmitField('Create')

class CreateProposalForm(FlaskForm):
    template_id = SelectField('Template', coerce=int)
    params = TextAreaField('Parameters', default="[]")
    parties = TextAreaField('Parties', default="[]")
    submit = SubmitField('Create')

class CloneProposalForm(FlaskForm):
    template_id = SelectField('Template', coerce=int)
    params = HiddenField('Parameters', default="[]")
    submit = SubmitField('Clone')

