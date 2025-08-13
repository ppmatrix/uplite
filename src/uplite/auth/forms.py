"""Authentication forms for UpLite."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from ..models.user import User


class LoginForm(FlaskForm):
    """Login form."""
    
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={'placeholder': 'Enter your username', 'class': 'form-control'}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter your password', 'class': 'form-control'}
    )
    remember_me = BooleanField(
        'Remember Me',
        render_kw={'class': 'form-check-input'}
    )
    submit = SubmitField(
        'Sign In',
        render_kw={'class': 'btn btn-primary w-100'}
    )


class RegisterForm(FlaskForm):
    """Registration form."""
    
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters.')
        ],
        render_kw={'placeholder': 'Choose a username', 'class': 'form-control'}
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message='Please enter a valid email address.'),
            Length(max=120)
        ],
        render_kw={'placeholder': 'Enter your email', 'class': 'form-control'}
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6, message='Password must be at least 6 characters long.')
        ],
        render_kw={'placeholder': 'Choose a password', 'class': 'form-control'}
    )
    password2 = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ],
        render_kw={'placeholder': 'Confirm your password', 'class': 'form-control'}
    )
    submit = SubmitField(
        'Register',
        render_kw={'class': 'btn btn-primary w-100'}
    )
    
    def validate_username(self, username):
        """Validate username uniqueness."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """Validate email uniqueness."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')
