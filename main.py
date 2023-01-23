import sqlite3
import os
from FDataBase import FDataBase
from flask import redirect, render_template, Flask, request, flash, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


# CONFIGURATION
DATABASE = "posts.db"
SECRET_KEY = "a;df32;klj asdf 2323"
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "posts.db")))


db = False
@app.before_request
def check_connt():
    global db
    db_c = create_db()
    db = FDataBase(db_c)


def connect_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db_ = connect_db()
    with app.open_resource("sq_db.sql", mode='r') as f:
        db_.cursor().executescript(f.read())
    db_.commit()
    return db_

@app.errorhandler(404)
def handle_bad_request(e):
    return '<h1>bad request!</h1>', 400


@app.route("/")
def handler():
    return render_template("index.html", title="FlaskSite", menu=db.getMenu()[::-1])


@app.route("/add_post", methods=["GET", "POST"])
def AddPost():
    print(url_for('handler'))
    if request.method == "POST":
        if db.addContent(request.form) == 200:
            flash("Пост опубликован", category="success")
        else:
            flash("Ошибка", category="error")
    return render_template("add_menu.html")


@app.route("/edit_post<int:post_id>", methods=["POST", "GET"])
def editor(post_id):
    if request.method == 'GET':
        menu = db.getContent(post_id)
        return render_template("edit.html", content=menu[-1]["content"], post_num=post_id)
    code = db.edit_post(request.form["new_content"], post_id)
    if code == 200:
        flash("Правки внесены", category="success")
    else:
        flash("Ошибка", category="error")

    menu = db.getContent(post_id)

    return render_template("edit.html", content=menu[-1]["content"], post_num=post_id)

@app.route("/<int:post_id>")
def showPost(post_id):
    respone = db.getPost(post_id)
    print(post_id, respone)
    if not respone:
        abort(404)
    return render_template("post_skeleton.html", id=respone["id"],
                           content=respone["content"], title=respone["title"], 
                           authour=respone["authour"])

@app.route("/delete_post<int:post_id>")
def delete_post(post_id):
    db.deletePost(post_id)
    return render_template("deletePage.html", title="Удаление поста")

@app.route('/profile')
def profile():
    return render_template("authorization.html")

@app.route("/reqistration", methods=["GET", "POST"])
def reg():
    if len(request.form['login']) < 6 and len(request.form['password']) < 6:
        flash("Неверно введены данные", category="error")
        return render_template("authorization.html")

    if not db.checkin(request.form['login']):
        psw = generate_password_hash(request.form["password"])
        code = db.newUser(psw, request.form["login"])
        if code == 200:
            flash("Вы успешно зарегистрировались", category="success")
        else:
            flash("Ошибка во время регистрации", category="error")
        return render_template("authorization.html")
    else:
        if check_password_hash(db.returnHsh(request.form["login"]), request.form["password"]):
            flash("Вы вошли в учетную запись", category="success")
            return render_template("authorization.html")
        else:
            flash("Неверный пароль", category="error")
            return render_template("authorization.html")

if __name__ == "__main__":
    app.run(debug=True)
