from flask import Flask, url_for
from datetime import datetime
from flask import render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import login_user
from loginform import LoginForm
from data import db_session
from data.users import User
from data.product import Product
from forms.user import RegisterForm
from flask_login import login_required
from flask_login import current_user
from flask_login import logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from forms.product import ProductForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Main(db.Model):
    id_object = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(300), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    pictures = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Main {self.id_object}>'


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def start():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        product = db_sess.query(Product).filter(Product.id == 2)
    return render_template("main.html", title='TopSwap', a=product)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            patronymic=form.patronymic.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/help')
def help():
    return render_template('main.html')


@app.route('/product_add', methods=['GET', 'POST'])
@login_required
def add_news():
    form = ProductForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = Product(
            title=form.title.data,
            content=form.content.data,
        )
        db_sess.add(product)
        db_sess.commit()
        return redirect('/')
    return render_template('product.html', title='Добавление записи',
                           form=form)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1', debug=True)
