from flask import Flask, render_template, redirect, url_for
from data import db_session
from data.users import User
from data.products import Products
from data.baskets import Basket
from forms.user import RegisterForm, LoginForm, BuyForm, PayForm
from flask_login import LoginManager, login_user, login_required, logout_user
import os
import sys
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
category = [('Розыгрыши', 'fun'), ('Съедобные', 'eat'), ('Взрывы, фейерверки', 'bang'), ('Товары для девочек', 'girl'),
            ('Безопасность', 'safe'), ('Другое', 'another')]
user_id = 0
addresses = ['Bolshoy Znamensky Lane, 8к2', 'Khamovnichesky Val Street, 26']


def get_coords(name):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={name}&format=json"
    geo_response = requests.get(geocoder_request)
    if geo_response:
        json_response = geo_response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        coords = toponym["Point"]["pos"].replace(' ', ',')
        return coords


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
            basket = db_sess.query(Basket).filter(Basket.user_id == user.id).all()
            for i in basket:
                if not i.pay:
                    break
            else:
                new_basket = Basket()
                new_basket.user_id = user.id
                db_sess.add(new_basket)
                db_sess.commit()
            global user_id
            user_id = user.id
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


def pay(user_id):
    db_sess = db_session.create_session()
    basket = db_sess.query(Basket).filter(Basket.user_id == user_id, Basket.pay == 0).first()
    if basket.composition:
        basket.pay = True
        new_basket = Basket()
        new_basket.user_id = user_id
        db_sess.add(new_basket)
        db_sess.commit()
    return redirect('/account')


@app.route('/account', methods=['GET', 'POST'])
def account():
    form = PayForm()
    if form.validate_on_submit():
        return pay(user_id)

    db_sess = db_session.create_session()
    products = []

    current_basket = db_sess.query(Basket).filter(Basket.user_id == user_id, Basket.pay == 0).first().composition
    if current_basket:
        busket_list = list(map(int, current_basket.split(',')))
        summa_basket = 0
        for i in busket_list:
            products.append(db_sess.query(Products).filter(Products.id == i).first().title)
            summa_basket += db_sess.query(Products).filter(Products.id == i).first().cost
    else:
        products.append('Корзина пока пуста, купите что-нибудь')
        summa_basket = 0

    baskets = db_sess.query(Basket).filter(Basket.user_id == user_id, Basket.pay == 1).all()
    baskets_list = []
    for i in baskets:
        summa_basket1 = 0
        products1 = []
        if i.composition:
            busket_list1 = list(map(int, i.composition.split(',')))
            for j in busket_list1:
                products1.append(db_sess.query(Products).filter(Products.id == j).first().title)
                summa_basket1 += db_sess.query(Products).filter(Products.id == j).first().cost
            baskets_list.append((', '.join(products1), summa_basket1))
    if not baskets:
        baskets_list = None
    return render_template('account.html', title='Аккаунт', baskets=baskets_list,
                           current_basket=(products, str(summa_basket)), form=form)


@app.route('/contact')
def contact():
    points = []
    for i in addresses:
        coord = get_coords(i)
        points.append(coord + ',pm2bll')
    map_params = {
        "l": "map",
        "pt": '~'.join(points)
    }
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_api_server)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    map_file = "static/map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
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
        if category[i.category_id - 1][0] == c:
            product1.append(i)
    return render_template('catalog.html', name=name, title=c, products=product1, category=category)


def buy(user_id, product_id):
    db_sess = db_session.create_session()
    new_basket = db_sess.query(Basket).filter(Basket.user_id == user_id, Basket.pay == 0).first()
    if new_basket.composition:
        basket_comp = new_basket.composition.split(',')
        basket_comp.append(str(product_id))
        new_basket.composition = ','.join(basket_comp)
    else:
        new_basket.composition = str(product_id)
    db_sess.commit()
    return redirect('/product/' + str(product_id))


@app.route('/product/<id>', methods=['GET', 'POST'])
def product(id):
    form = BuyForm()
    if form.validate_on_submit():
        return buy(user_id, id)
    db_sess = db_session.create_session()
    product = db_sess.query(Products).get(id)
    return render_template('product.html', product=product, title=product.title, form=form)


if __name__ == '__main__':
    db_session.global_init("db/shop.db")
    app.run(port=8000, host='127.0.0.1')
