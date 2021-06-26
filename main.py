from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.sqlite'

db = SQLAlchemy(app)


class Task(db.Model):
    # テーブルの設定
    __tablename__ = "tasks"

    # カラムの設定
    taskid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.String(100))
    title = db.Column(db.String(50))
    memo = db.Column(db.String(1000))
    date = db.Column(db.String(20))
    place = db.Column(db.String(300))


# データベースの生成
db.create_all()

# localhostにアクセスしたときの処理
@app.route('/')
def index():
    # templatesのindex.htmlでタスクを全て表示
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)

# localhost/createにpostされた時の処理
@app.route('/create', methods=["POST"])
def new():
    # 入力されたデータでタスクを追加してindexにリダイレクト
    task = Task()
    task.userid = request.form["userid"]
    task.title = request.form["title"]
    task.memo = request.form["memo"]
    task.date = request.form["date"]
    task.place = request.form["place"]
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))

# 編集ボタンが押された時の処理
@app.route('/edit', methods=["POST"])
def edit():
    # 選択されたタスクの編集画面へ遷移
    taskid = request.form["taskid"]
    task = Task.query.filter_by(taskid=taskid).first()
    return render_template("edit.html", task=task)

# 編集画面からpostされた時の処理
@app.route('/update', methods=["POST"])
def update():
    # 編集後のデータを設定してindexにリダイレクト
    taskid = request.form["taskid"]
    task = Task.query.filter_by(taskid=taskid).first()
    task.title = request.form["title"]
    task.memo = request.form["memo"]
    task.date = request.form["date"]
    task.place = request.form["place"]
    db.session.commit()
    return redirect(url_for('index'))

# localhostにアクセスしたとき
@app.route('/delete', methods=["POST"])
def delete():
    # 選択されたタスクを削除してindexにリダイレクト
    taskid = request.form["taskid"]
    task = Task.query.filter_by(taskid=taskid).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    # サーバの設定 address:localhost port:8001
    app.run(debug=True, host=os.getenv('APP_ADDRESS', 'localhost'), port=8001)
