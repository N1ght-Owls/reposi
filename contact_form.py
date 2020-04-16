from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

style = {'class': 'form-control'}
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw=style)
    email = EmailField('Email', validators=[DataRequired()], render_kw=style)
    message = StringField('Message', widget=TextArea(), validators=[DataRequired()], render_kw={'class': 'form-control', 'placeholder': 'Your message'})
    submit = SubmitField('Send', render_kw={'class': 'btn btn-primary'})