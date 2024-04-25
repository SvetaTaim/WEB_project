from flask import Flask, render_template


app = Flask(__name__)


@app.route('/home')
def home():
    return render_template('home.html', title='Всевозможные волшебные вредилки')


@app.route('/about')
def about():
    return render_template('about.html', title='О нас')


@app.route('/registrar')
def registrar():
    return render_template('registrar.html', title='Регистрация')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')