from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
import re

# Custom validator for password strength, aligned with NIS2 recommendations
def password_strength(form, field):
    password = field.data
    min_length = 12  # Recommended minimum length for NIS2
    if len(password) < min_length:
        raise ValidationError(f'Password must be at least {min_length} characters long.')

    # Must contain at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')

    # Must contain at least one lowercase letter
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')

    # Must contain at least one number
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must contain at least one number.')

    # Must contain at least one special character
    # Including some common special characters. You can modify these if you have specific requirements.
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|]', password):
        raise ValidationError('Password must contain at least one special character (e.g., !@#$%^&*).')

    # Optional: You can add more checks here, e.g., to avoid common passwords
    common_passwords = ['password', '123456', 'qwerty', 'admin', 'test']
    if password.lower() in common_passwords:
        raise ValidationError('This password is too common. Please choose a more complex one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', 
                                 validators=[DataRequired(), password_strength]) # Apply the custom validator
    confirm_password = PasswordField('Confirm New Password', 
                                     validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Change Password')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    # Apply the custom validator here for new user creation
    password = PasswordField('Password', validators=[DataRequired(), password_strength]) 
    profile = SelectField('Profile', choices=[('user', 'Standard User'), ('editor', 'Editor'), ('admin', 'Administrator')], validators=[DataRequired()])
    submit = SubmitField('Save User')