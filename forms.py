from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    gender = RadioField('Пол', choices=[('male', 'Мужчина'), ('female', 'Женщина')])
    remember_me = BooleanField('Запомнить меня')
    image = FileField('Загрузить аватар', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Зарегистрироваться')


class AddNewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('О чем вы хотите рассказать', validators=[DataRequired()])
    image = FileField('Загрузить изображение', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Добавить')


class FindFriendsForm(FlaskForm):
    name = StringField('Найти по имени', validators=[DataRequired()])
    submit = SubmitField('Найти')


class MessageForm(FlaskForm):
    content = TextAreaField('Сообщение:', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class EditProfileForm(FlaskForm):
    username = StringField('Изменить имя')
    gender = RadioField('Пол', choices=[('male', 'Мужчина'), ('female', 'Женщина')])
    image = FileField('Изменить аватар', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    status = TextAreaField('Краткая информация о вас')
    submit = SubmitField('Подтвердить')
