import sqlite3
import os
from FDataBase import FDataBase
from flask import redirect, render_template, Flask, request, flash, abort, \
    url_for, make_response, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta
from flask_login import LoginManager, login_user, login_required, \
    current_user, logout_user
from User import UserInfo
import re

# CONFIGURATION
DATABASE = "posts.db"
SECRET_KEY = "2c4d969558ce80c318380969f35ebb"
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "posts.db")))
# Длительность сеанса
app.permanent_session_lifetime = timedelta(days=1)
login_manager = LoginManager(app)
login_manager.login_view = 'reg'
login_manager.login_message = 'Нужно войти или зарегистрироваться'
login_manager.login_message_category = 'success'
db = False


@app.route("/")
def handler():
    '''Главная страница'''
    name = 'не авторизован'  # Имя пользователя(User name)
    img = ''
    if current_user.get_id() == 'Алим':
        img = '2'
    if 'userID' in session:  # Если открыта сессия
        name = session['userID'][1]
    elif not current_user.is_active:
        logout_user()
    return render_template("index.html", img=img, title="FlaskSite", menu=db.getMenu()[::-1], UserName=name)


@login_manager.user_loader
def load_user(userID):
    return UserInfo(userID, db)


@app.before_request
def establish_connection():
    '''Функция для установления соединения с БД'''
    global db   # доступ к БД через объект FDataFase
    try:
        # обращение к БД, через путь указанный в приложении
        connection = sqlite3.connect(app.config["DATABASE"])
        connection.row_factory = sqlite3.Row  # Вид словарь
        # проверка наличия таблицы
        with app.open_resource("sq_db.sql", mode='r') as file:
            connection.cursor().executescript(file.read())
        connection.commit()  # сохранить изменения
        db = FDataBase(connection)  # установить соединение
    except Exception as error:
        print('Ошибка была обнаружена ', error)


@app.errorhandler(404)
def handle_bad_request(e):
    return '<h1>bad request!</h1>', 400


@app.route('/search_post', methods=["POST"])
def search():
    menu = db.getMenu()
    query = request.form['query']
    results = []
    search_d = [query.split()[:i] for i in range(len(query.split()), 1, -1)]
    search_d += [[item] for item in query.split()]
    for elem in menu:
        for row in search_d:
            if len(row) < 2: pattern = f'{"".join(row)}'
            else: pattern = f'{" ".join(row)}'
            if re.search(pattern, elem['title']):
                indices = re.finditer(pattern, elem['title'])
                title=[elem['title'][:ind.start()]+'<p class="marker">'+\
                               elem['title'][ind.start():ind.end()]+'</p>'+\
                               elem['title'][ind.end():] for ind in indices]

                results.append([title, elem])
                break
    return render_template('search_res.html', menu=results)

@app.route("/add_post", methods=["GET", "POST"])
@login_required
def AddPost():
    if request.method == "POST":
        if db.addContent(request.form, current_user.get_ID()) == 200:
            flash("Пост опубликован", category="success")
        else:
            flash("Ошибка", category="error")
    return render_template("add_menu.html")


@app.route("/edit_post<int:post_id>", methods=["POST", "GET"])
@login_required
def editor(post_id):
    if current_user.is_active and db.getPost(post_id)['authour_id'] == \
     current_user.get_ID() or current_user.get_id() == 'Алим':
        if request.method == 'GET':
            menu = db.getContent(post_id)
            return render_template("edit.html", content=menu[-1]["content"], post_num=post_id)
        code = db.edit_post(request.form["new_content"], post_id)
        if code == 200:
            # данные внесены без ошибок код 200
            flash("Правки внесены", category="success")
        else:
            # во время записи произошла ошибка
            flash("Ошибка", category="error")
        menu = db.getContent(post_id)

        return render_template("edit.html", content=menu[-1]["content"], post_num=post_id)
    abort(404)

@app.route("/<int:post_id>")
def showPost(post_id):
    respone = db.getPost(post_id)
    if current_user.is_active and db.getPost(post_id)['authour_id'] == \
            current_user.get_ID() or current_user.get_id() == 'Алим':
        return render_template("post_skeleton_full.html", id=respone["id"],
                               content=respone["content"], title=respone["title"], 
                               authour=respone["authour"])
    if not respone:
        abort(404)
    return render_template("post_skeleton.html", id=respone["id"],
                           content=respone["content"], title=respone["title"], 
                           authour=respone["authour"])


@app.route("/delete_post<int:post_id>")
@login_required
def delete_post(post_id):
    if current_user.is_active and db.getPost(post_id)['authour_id'] == \
     current_user.get_ID() or current_user.get_id() == 'Алим':
        db.deletePost(post_id)
        return render_template("deletePage.html", title="Удаление поста")
    abort(401)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('handler'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.get_id() == 'Алим':
        return render_template("Personal Area.html", name=current_user.name, menu=db.getMenu())
    elif current_user.is_active:
        return render_template("Personal Area.html", name=current_user.name, \
            menu=db.getMenu(current_user.get_ID())[::-1])
        # menu=db.getMenu(current_user.get_ID())[::-1])
    return render_template("authorization.html")


@app.route("/reqistration", methods=["GET", "POST"])
def reg():
    session.permanent = True
    if request.method != 'GET':
        if len(request.form['login']) < 5 and len(request.form['password']) < 8:
            flash("Неверно введены данные", category="error")
            return render_template("authorization.html")

        if not db.checkin(request.form['login']):
            psw = generate_password_hash(request.form["password"])
            code = db.newUser(psw, request.form["login"])
            if code == 200:
                session['userID'] = db.getUserId(request.form['login'])
                user = UserInfo(session['userID'][1], db)
                login_user(user)
                flash("Вы успешно зарегистрировались", category="success")
                return redirect(url_for('handler'))
            else:
                flash("Ошибка во время регистрации", category="error")
            return render_template("authorization.html")
        else:
            if check_password_hash(db.returnHsh(request.form["login"]), request.form["password"]):
                session['userID'] = db.getUserId(request.form['login'])
                user = UserInfo(session['userID'][1], db)
                login_user(user)
                flash("Вы вошли в учетную запись", category="success")
                return redirect(url_for('handler'))
            else:
                flash("Неверный пароль", category="error")
                return render_template("authorization.html")
    return render_template("authorization.html")


if __name__ == "__main__":
    app.run(debug=True)
