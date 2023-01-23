from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
# app["SECRET_KEY"] = ";lvmkakldshenb,..cznioer"
ALLOWED_EXTENSIONS = {'jpg', 'png'}
UPLOAD_FOLDER = '/'
app.config["UPLOAD_FOLDER"] = '/'

@app.route('/')
def func():
    return render_template("ind.html")

@app.route('/img', methods=["POST", "GET"])
def func2():

    return '<h1>Без ошибок</h1>'

if __name__ == "__main__":
    app.run(debug=True)
