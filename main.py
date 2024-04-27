from flask import Flask, render_template, redirect, url_for
from data import db_session
from data.users import User
from data.products import Products
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required ,logout_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
category = [('Розыгрыши', 'fun'), ('Съедобные', 'eat'), ('Взрывы, фейерверки', 'bang'), ('Товары для девочек', 'girl'), ('Безопасность', 'safe'), ('Другое', 'another')]
basket = []


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)



@app.route('/')
def index():
    return redirect("/home")

@app.route('/home')
def home():
    return render_template('home.html', title='Всевозможные волшебные вредилки')


@app.route('/about')
def about():
    return render_template('about.html', title='О нас')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            basket.clear()
            return redirect("/home")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Вход', form=form)


@app.route('/exit')
@login_required
def exit():
    logout_user()
    return redirect("/home")


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
            name=form.name.data,
            email=form.email.data,
        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/account')
def account():
    db_sess = db_session.create_session()
    products = db_sess.query(Products)
    return render_template('account.html', title='Аккаунт', products=products, basket=basket)


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Контакты')


@app.route('/catalog')
def catalog():
    db_sess = db_session.create_session()
    products = db_sess.query(Products)
    return render_template('catalog.html', title='Каталог', products=products, category=category)


@app.route('/catalog/<name>')
def catalog_new(name):
    db_sess = db_session.create_session()
    products = db_sess.query(Products)
    product1 = list()
    c = ''
    for i in category:
        if i[1] == name:
            c = i[0]
            break
    for i in products:
        if category[i.category - 1][0] == c:
            product1.append(i)
    return render_template('catalog.html', name=name, title=c, products=product1, category=category)


def buy(name):
    product, way = name.split('#')
    db_sess = db_session.create_session()
    products = db_sess.query(Products)
    basket.append(products[int(product) - 1])
    return catalog_new(way)


@app.route('/product/<id>')
def product(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Products).get(id)
    return render_template('product.html', product=product)



if __name__ == '__main__':
    db_session.global_init("db/shop.db")
    app.run(port=8000, host='127.0.0.1')


