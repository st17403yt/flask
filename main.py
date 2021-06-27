from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import urllib.request
import urllib.parse
import json
import hashlib
import urllib.request
import urllib.parse
import jwt
from jwt.algorithms import RSAAlgorithm

app = Flask(__name__)

# セッション情報の暗号化のための秘密鍵
app.config['SECRET_KEY'] = 'secret_key'

# DBのパス
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


class User(db.Model):
    __tablename__ = "users"
    # userid = sub
    userid = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(200))

# データベースの生成
db.create_all()

# localhostにアクセスしたときの処理
@app.route('/')
def index():
    # templatesのindex.htmlでタスクを全て表示
    if "userid" in session:
        tasks = Task.query.filter_by(userid=session["userid"])
        users = User.query.all()
        return render_template("index.html", tasks=tasks, name=session["name"], users=users)
    return render_template("login.html")

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

###########################################
# ここからユーザ認証
###########################################


# クライアント情報
# 自身の環境に合わせて設定する。
# google cloud platform にて発行可能
client_id = '<client_id>.apps.googleusercontent.com'
client_secret = '<client_secret>'
redirect_uri = 'http://localhost:5000/callback'

# id_token 検証用公開鍵
# https://www.googleapis.com/oauth2/v3/certs
# 下のやつを使ったら行けた
jwk_json = {
    "alg": "RS256",
    "n": "rH9e4LpeORtRkQuo5vKL-csLPnJmyWU_qHiOqWyXVsoPymUKImNsPlabOcvkYYlPflWE-qmtQCH-ACDjxzChyIktr-5zeCEZidln8pWEmDq-R-aXi_sQgJUr-7H_Y69hD8cR0K3LyC86QRbpigxW8F6hUU9aj_9VWuVwsMvLiQnbbzS4CWvi_WzIW9iG0gOthsslffa_6rqoQpHc0GfsEu3e971QZcJyMxr6ptY_bvTwIYqwRv9ptxtKTMqovV6YBN5n_LhCDmk1gBLmSej6mfHSW2io6TXZaV3PayL2UTte6qrvAkF_RXUtVeuDxm4scUe1Rdf-TdsAXFm1KPNq4w",
    "kid": "112e4b52ab833017d385ce0d0b4c60587ed25842",
    "e": "AQAB",
    "kty": "RSA",
    "use": "sig"
}
public_key = RSAAlgorithm.from_jwk(jwk_json)

# iss(トークン発行者)
issuer = 'https://accounts.google.com'

# Google エンドポイント
authorization_base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
token_url = 'https://www.googleapis.com/oauth2/v4/token'


# 認可リクエスト用
@app.route("/login", methods=["POST"])
def login():
    # nonce、stateの生成と保存
    nonce = hashlib.sha256(os.urandom(32)).hexdigest()
    state = hashlib.sha256(os.urandom(32)).hexdigest()
    session['nonce'] = nonce
    session['state'] = state
    # Googleへの認可リクエスト
    return redirect(authorization_base_url+'?{}'.format(urllib.parse.urlencode({
        'client_id': client_id,
        'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
        'redirect_uri': redirect_uri,
        'state': state,
        'nonce': nonce,
        'response_type': 'code'
    })))


# 認可レスポンス用リダイレクションエンドポイント + トークンリクエスト用
@app.route("/callback")
def callback():
    # state 検証
    state = request.args.get('state')
    if state != session['state']:
        print("invalid_redirect")
    code = request.args.get('code')
    # トークンリクエスト
    body = urllib.parse.urlencode({
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }).encode('utf-8')

    req = urllib.request.Request(token_url)
    with urllib.request.urlopen(req, data=body) as f:
        res = f.read()

    # id_token 検証
    content = json.loads(res)
    id_token = content['id_token']
    claims = jwt.decode(id_token,
                        public_key,
                        issuer=issuer,
                        audience=client_id,
                        algorithms=["RS256"])

    # nonce 検証
    if claims['nonce'] != session['nonce']:
        return "invalid id_token"

    # claimsのsubは全てのGoogleアカウントで一意
    session["userid"] = claims["sub"]
    session["name"] = claims["name"]
    user = User()
    user.email = claims["email"]
    user.userid = claims["sub"]
    user.username = claims["name"]
    db.session.add(user)
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    # サーバの設定 address:localhost port:5000
    app.run(debug=True, host=os.getenv('APP_ADDRESS', 'localhost'), port=5000)
