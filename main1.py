from db import *
from flask import Flask, render_template, redirect, session, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db = DB()


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')

class AddNewsForm(FlaskForm):
    title = StringField('Заголовок новости', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    submit = SubmitField('Добавить')

class MessageForm(FlaskForm):
    content = TextAreaField('Сообщение:', validators=[DataRequired()])
    submit = SubmitField('Отправить')

class PhotoForm(FlaskForm):
    photo = FileField('Загрузить иконку', validators=[FileRequired()])



@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(user_name)
        if not (exists[0]) and user_name != 'admin':
            user_model.insert(user_name, password)
            # exists = user_model.exists(user_name, password)
            # session['username'] = user_name
            # session['user_id'] = exists[1]
        return redirect("/index")
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
        return redirect("/index")
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/login')
    users = UsersModel(db.get_connection())
    news1 = NewsModel(db.get_connection()).get_all()
    news = []
    for i in news1:
        news.append(list(i) + [users.get(i[3])[1]])
    return render_template('index.html', username=session['username'],
                           news=news, admin=session['username'] == 'admin')


@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect('/login')
    table = []
    users = UsersModel(db.get_connection()).get_all()
    news = NewsModel(db.get_connection())
    for user in users:
        data_user = news.get_all(user[0])
        print(data_user)
        table.append([user[1], len(data_user)])
    return render_template('info.html', username=session['username'],
                           table=table, admin=session['username'] == 'admin')


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        nm = NewsModel(db.get_connection())
        nm.insert(title, content, session['user_id'])
        return redirect("/index")
    return render_template('add_news.html', title='Добавление новости',
                           form=form, username=session['username'])


@app.route('/messages/<int:id_to>', methods=['GET', 'POST'])
def messages(id_to):
    if 'username' not in session:
        return redirect('/login')
    messages = MessagesModel(db.get_connection()).get_all(session['user_id'], id_to)
    user_name = UsersModel(db.get_connection()).get(id_to)[1]
    data = []
    for i in messages:
        message = [i[0], i[1], i[2], UsersModel(db.get_connection()).get(i[1])[1], i[3], i[4][:-7]]
        data.append(message)
    form = MessageForm()
    if form.validate_on_submit():
        content = form.content.data
        nm = MessagesModel(db.get_connection())
        nm.insert(session['user_id'], id_to, content)
        return redirect("/messages/{}".format(str(id_to)))
    return render_template('messages.html', messages=data,
                           form=form, username=session['username'], user=user_name)


@app.route('/users_messages')
def users_messages():
    if 'username' not in session:
        return redirect('/login')
    users = UsersModel(db.get_connection()).get_all()
    users_mes = []
    for i in users:
        if i[1] != session['username']:
            users_mes.append([i[0], i[1]])
    return render_template('users_messages.html', username=session['username'],
                           users_mes=users_mes, admin=session['username'] == 'admin')


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    nm.delete(news_id)
    return redirect("/index")

@app.route('/user_page')
def user_page():
    if 'username' not in session:
        return redirect('/login')
    users = UsersModel(db.get_connection())
    news1 = NewsModel(db.get_connection()).get_all(session['user_id'])
    news = []
    for i in news1:
        news.append(list(i) + [users.get(i[3])[1]])
    return render_template('index.html', username=session['username'],
                           news=news, admin=session['username'] == 'admin')

@app.route('/set_icon/{int:user_id}', methods=['GET', 'POST'])
def set_icon(user_id):
    if 'username' not in session:
        return redirect('/login')
    form = PhotoForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        if filename.split('.')[-1] in ['png', 'jpeg', 'jpg', 'gif']:
            f.save('/static/images/icons/{}'.format(str(user_id) + filename.split()[-1]))
            return redirect('/user_page')
    return render_template('set_icon.html', form=form)


if __name__ == '__main__':
    db = DB()
    user_model = UsersModel(db.get_connection())
    user_model.init_table()
    news_model = NewsModel(db.get_connection())
    news_model.init_table()
    messages_model = MessagesModel(db.get_connection())
    messages_model.init_table()
    app.run(port=8080, host='127.0.0.1')
