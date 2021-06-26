from flask import Flask, render_template, request, redirect, url_for, Markup
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.sqlite'

db = SQLAlchemy(app)


class Task(db.Model):

    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text())
    status = db.Column(db.Integer)


db.create_all()


@app.route('/')
def index():
    tasks = Task.query.all()
    # return render_template("index.html", tasks=tasks)

    html = """
    <div id="title" class="title">タスク</div>
    <form name="f" method="post">
      <div class="text_area"><input type="text" name="new_text" id="new_text"></div>
      <table>
    """
    for task in tasks:
        html = html + f"""
        <tr>
          <td
            class="card"
            id="task_{task.id}"
            task_id="{task.id}">{ task.text }
          </td>
        </tr>
        """
    html = html + """
      </table>
    </form>
    """

    return Markup(html)


@app.route('/new', methods=["POST", "GET"])
def new():
    task = Task()
    task.text = request.form["new_text"]
    task.status = 0
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))


app.run(debug=True)
