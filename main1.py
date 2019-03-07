from flask import Flask, render_template, redirect, session, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired
from random import randint
from werkzeug.utils import secure_filename
import sqlite3
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy(app)


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Images {} {}>'.format(
            self.id, self.data)


class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1 = db.Column(db.Integer)
    user2 = db.Column(db.Integer)

    def __repr__(self):
        return '<Friends {} {}>'.format(
            self.id, self.user1, self.user2)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), unique=False, nullable=False)
    avatar_id = db.Column(db.Integer)
    gender = db.Column(db.String(20), unique=False, nullable=False)
    about = db.Column(db.String(256), unique=False)

    def __repr__(self):
        return '<User {} {} {} {} {} {}>'.format(
            self.id, self.username, self.password_hash, self.avatar_id, self.age, self.gender, self.about)


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    content = db.Column(db.String(1000), unique=False, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    date_time = db.Column(db.DateTime, unique=False, nullable=False)
    image_id = db.Column(db.Integer)

    def __repr__(self):
        return '<News {} {} {} {} {}>'.format(
            self.id, self.title, self.content, self.user_id, self.date_time)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), unique=False, nullable=False)
    id_from = db.Column(db.Integer, nullable=False)
    id_to = db.Column(db.Integer, nullable=False)
    date_time = db.Column(db.DateTime, unique=False, nullable=False)

    def __repr__(self):
        return '<Message {} {} {} {} {}>'.format(
            self.id, self.content, self.id_from, self.id_to, self.date_time)


db.create_all()


def abort_if_news_not_found(news_id):
    if not User.query.filter_by(id=news_id):
        abort(404, message="News {} not found".format(news_id))


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


class MessageForm(FlaskForm):
    content = TextAreaField('Сообщение:', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class PhotoForm(FlaskForm):
    photo = FileField('Загрузить иконку', validators=[FileRequired()])

def generate_number():
    num = ''
    for _ in range(10):
        num += str(randint(0, 9))
    return num


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        gender = form.gender.data
        f = User.query.filter_by(username=user_name).first()
        if not f and user_name != 'admin':
            file = form.image.data
            if file:
                name = 'static/images/icons/{}'.format(generate_number() + file.filename)
                newFile = Images(
                    data=name
                )
                file.save(name)
                db.session.add(newFile)
                db.session.commit()
            else:
                if gender == 'male':
                    name = 'static/images/icons/avatar1.png'
                else:
                    name = 'static/images/icons/avatar2.png'
                newFile = Images(
                    data=name
                )
                db.session.add(newFile)
                db.session.commit()
            user = User(username=user_name,
                        password_hash=password,
                        avatar_id=newFile.id,
                        gender=gender
                        )
            db.session.add(user)
            db.session.commit()
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
        f = User.query.filter_by(username=user_name, password_hash=password).first()
        if f:
            session['username'] = user_name
            session['user_id'] = f.id

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
    news1 = reversed(News.query.order_by(News.date_time).all())
    news = []
    #    user_avatar = Images.query.filter_by(id=User.query.filter_by(id=session('user_id')).first().avatar_id).first().data
    for i in news1:
        avatar = Images.query.filter_by(id=User.query.filter_by(id=i.user_id).first().avatar_id).first().data
        gender = User.query.filter_by(id=i.user_id).first().gender
        image = Images.query.filter_by(id=i.image_id).first()
        if image:
            image = image.data
        else:
            image = 0
        news.append(
            [User.query.filter_by(id=i.user_id).first().username, i.id, i.title, i.content, i.user_id, str(i.date_time),
             image, avatar, gender])
    return render_template('index.html', username=session['username'],
                           news=news, admin=session['username'] == 'admin')


# @app.route('/admin')
# def admin():
#     if 'username' not in session:
#         return redirect('/login')
#     table = []
#     users = UsersModel(db.get_connection()).get_all()
#     news = NewsModel(db.get_connection())
#     for user in users:
#         data_user = news.get_all(user[0])
#         print(data_user)
#         table.append([user[1], len(data_user)])
#     return render_template('info.html', username=session['username'],
#                            table=table, admin=session['username'] == 'admin')
#
#
@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        file = form.image.data
        if file:
            name = 'static/images/news/{}'.format(generate_number() + file.filename)
            newFile = Images(
                data=name
            )
            file.save(name)
            db.session.add(newFile)
            db.session.commit()
        else:
            class Object():
                pass

            newFile = Object()
            newFile.id = 0
        title = form.title.data
        content = form.content.data
        news = News(title=title,
                    content=content,
                    user_id=session['user_id'],
                    date_time=datetime.datetime.now(),
                    image_id=newFile.id)
        db.session.add(news)
        db.session.commit()
        return redirect("/index")
    return render_template('add_news.html', title='Добавление новости',
                           form=form, username=session['username'])


@app.route('/messages/<int:id_to>', methods=['GET', 'POST'])
def messages(id_to):
    if 'username' not in session:
        return redirect('/login')
    messages = reversed(Message.query.filter((Message.id_to == session['user_id'] and Message.id_from == id_to) | (
        Message.id_to == id_to and Message.id_from == session['user_id'])).order_by(Message.date_time).all())
    data = []
    for i in messages:
        message = [i.id, i.id_from, i.id_to, User.query.filter(User.id == id_to).first().username, i.content,
                   str(i.date_time)[:-7]]
        data.append(message)
    form = MessageForm()
    if form.validate_on_submit():
        content = form.content.data
        nm = Message(content=content, id_from=session['user_id'], id_to=id_to, date_time=datetime.datetime.now())
        db.session.add(nm)
        db.session.commit()
        return redirect("/messages/{}".format(str(id_to)))
    return render_template('messages.html', messages=data,
                           form=form, username=session['username'],
                           user=User.query.filter(User.id == id_to).first().username)


@app.route('/users_messages')
def users_messages():
    if 'username' not in session:
        return redirect('/login')
    users = User.query.all()
    users_mes = []
    for i in users:
        if i.username != session['username']:
            users_mes.append([i.id, i.username])
    return render_template('users_messages.html', username=session['username'],
                           users_mes=users_mes, admin=session['username'] == 'admin')


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    news = News.query.filter_by(id=news_id).first()
    db.session.delete(news)
    db.session.commit()
    return redirect("/index")


@app.route('/make_friend/<int:user_id>', methods=['GET'])
def make_friend(user_id):
    if 'username' not in session:
        return redirect('/login')
    f1 = Friends.query.filter_by(user1=session['user_id'], user2=user_id).first()
    f2 = Friends.query.filter_by(user1=user_id, user2=session['user_id']).first()
    if not f1 or f2:
        friends = Friends(
            user1=session['user_id'],
            user2=user_id)
        db.session.add(friends)
        db.session.commit()
    else:
        if f1:
            db.session.delete(f1)
            db.session.commit()
        elif f2:
            db.session.delete(f2)
            db.session.commit()
    return redirect("/user_page/{}".format(str(user_id)))


@app.route('/friends')
def friends():
    if 'username' not in session:
        return redirect('/login')
    users = User.query.all()
    people = []
    for i in users:
        if i.id != session['user_id']:
            friend = Friends.query.filter((Friends.user1==i.id) | (Friends.user2==i.id)).first()
            if friend:
                avatar = Images.query.filter_by(id=i.avatar_id).first().data
                people.append([i.id, i.username, avatar])
    return render_template('friends.html', username=session['username'],
                           people=people, admin=session['username'] == 'admin')


@app.route('/user_page/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    if 'username' not in session:
        return redirect('/login')
    news1 = list(reversed(News.query.order_by(News.date_time).all()))
    news = []
    user_name = User.query.filter_by(id=user_id).first().username
    avatar = Images.query.filter_by(id=User.query.filter_by(id=user_id).first().avatar_id).first().data
    #    user_avatar = Images.query.filter_by(id=User.query.filter_by(id=session('user_id')).first().avatar_id).first().data
    f1 = Friends.query.filter_by(user1=session['user_id'], user2=user_id).first()
    f2 = Friends.query.filter_by(user1=session['user_id'], user2=user_id).first()
    if f1 or f2:
        make = False
    else:
        make = True
    for i in news1:
        if i.user_id == user_id:
            print(avatar)
            gender = User.query.filter_by(id=i.user_id).first().gender
            image = Images.query.filter_by(id=i.image_id).first()
            if image:
                image = image.data
            else:
                image = 0
            news.append([User.query.filter_by(id=i.user_id).first().username, i.id, i.title, i.content, i.user_id,
                         str(i.date_time), image, avatar, gender])
    print(make)
    return render_template('user_page.html', profile_name=user_name, username=session['username'],
                           news=news, admin=session['username'] == 'admin', avatar=avatar, user_id=user_id, make=make)



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
