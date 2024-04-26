from flask import Flask, render_template


app = Flask(__name__)


@app.route('/home')
def home():
    return render_template('home.html', title='Всевозможные волшебные вредилки')


@app.route('/about')
def about():
    return render_template('about.html', title='О нас')


@app.route('/login')
def login():
    return render_template('login.html', title='Вход')


@app.route('/register')
def register():
    return render_template('register.html', title='Регистрация')


@app.route('/<username>')
def user(username):
    return render_template('user.html', title='Вход', name=username)


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Контакты')


@app.route('/category')
def category():
    return render_template('category.html', title='Категории')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')