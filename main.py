from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.sqlite'

db = SQLAlchemy(app)


class Task(db.Model):
    __tablename__ = "tasks"
    taskid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.String(100))
    title = db.Column(db.String(50))
    memo = db.Column(db.String(1000))
    date = db.Column(db.String(20))
    place = db.Column(db.String(300))


db.create_all()


@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)


@app.route('/create', methods=["POST"])
def new():
    task = Task()
    task.userid = request.form["userid"]
    task.title = request.form["title"]
    task.memo = request.form["memo"]
    task.date = request.form["date"]
    task.place = request.form["place"]
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit', methods=["POST"])
def edit():
    taskid = request.form["taskid"]
    task = Task.query.filter_by(taskid=taskid).first()
    return render_template("edit.html", task=task)


@app.route('/update', methods=["POST"])
def update():
    taskid = request.form["taskid"]
    task = Task.query.filter_by(taskid=taskid).first()
    task.title = request.form["title"]
    task.memo = request.form["memo"]
    task.date = request.form["date"]
    task.place = request.form["place"]
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete', methods=["POST"])
def delete():
    taskid = request.form["taskid"]
    task = Task.query.filter_by(taskid=taskid).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, host=os.getenv('APP_ADDRESS', 'localhost'), port=8001)
