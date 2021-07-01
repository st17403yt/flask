from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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
import re
import string

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
        exists = db.session.query(User).filter_by(
            userid=session["userid"]).scalar() is not None
        if exists:
            tasks = Task.query.filter_by(userid=session["userid"])
            users = User.query.all()
            return render_template("index.html", tasks=tasks, name=session["name"], users=users)
    return render_template("login.html")


# localhost/createにpostされた時の処理
@app.route('/create', methods=["POST"])
def new():
    # 入力されたデータでタスクを追加してindexにリダイレクト
    task = Task()
    task.userid = session["userid"]
    task.title = request.form["title"]
    task.memo = request.form["memo"]
    date = request.form["date"].replace("-", "/")
    time = request.form["time"].replace(":", "/")
    task.date = date + "/" + time
    task.place = request.form["place"]
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))


# 編集ボタンが押された時の処理
@app.route('/edit', methods=["POST"])
def edit():
    # 選択されたタスクの編集画面へ遷移
    #taskid = request.form["taskid"]
    session["taskid"] = request.form["taskid"]
    task = Task.query.filter_by(taskid=session["taskid"]).first()
    temp = task.date.split("/")
    date = temp[0] + "-" + temp[1] + "-" + temp[2]
    time = temp[3] + ":" + temp[4]
    return render_template("edit.html", task=task, date=date, time=time)


# 編集画面からpostされた時の処理
@app.route('/update', methods=["POST"])
def update():
    # 編集後のデータを設定してindexにリダイレクト
    taskid = request.form["taskid"]
    task = Task.query.filter_by(taskid=taskid).first()
    task.title = request.form["title"]
    task.memo = request.form["memo"]
    date = request.form["date"].replace("-", "/")
    time = request.form["time"].replace(":", "/")
    task.date = date + "/" + time
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


# 住所入力時の補完機能
@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    if request.method == 'POST':
        data = request.get_data()
        input = escape(data.decode())
        ans = []
        pat = "^.*" + input + ".*$"
        count = 0
        ans, count = search(ans, pat, "./data/prefecture.txt", count)
        ans, count = search(ans, pat, "./data/city.txt", count)
        ans, count = search(ans, pat, "./data/town.txt", count)
        ans, count = search(ans, pat, "./data/block.txt", count)
        d = {}
        for i in range(count):
            d["value" + str(i)] = ans[i]
        return jsonify(d)


def search(ans, pat, file, count):
    f = open(file, "r", encoding="utf-8")
    a = f.read()
    data = a.splitlines()
    for i in data:
        if count > 5:
            break
        res = re.fullmatch(pat, i)
        if res != None:
            print(res.group(0))
            ans.append(res.group(0))
            count = count + 1
    f.close()
    return ans, count


def escape(text):
    symbol = string.punctuation
    table = str.maketrans("", "", symbol)
    result = text.translate(table)
    return result


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
    "e": "AQAB",
    "kty": "RSA",
    "use": "sig",
    "alg": "RS256",
    "kid": "b6f8d55da534ea91cb2cb00e1af4e8e0cdeca93d",
    "n": "3aOynmXd2aSH0ZOd0TIYd5RRaNXhLW306dlYw26nMp6QPGaJuOeMhTO3BO8Zt_ncRs4gdry4mEaUOetCKTUOyCCpIM2JAn0laN_iHfGKTYsNkjr16FiHWYJmvNJ1Q1-XXjWqNNKMFIKHKtMrsP2XPVD6ufp-lNQmt4Dl0g0qXJ4_Y_CKuP-uSlFWZuJ_0_2ukUgevvKtOZNcbth0iOiFalBRDr-2i1eNSJWOknEphy7GRs-JGPboTdHC7A3b-0dVFGMEMJFhxcEJHJgLCsQGdYdkphLJ5f21gCNdhp3g16H3Cqts2KTXgO4Rr8uhwZx5yiUjTuizD9wc7uDso4UJ7Q"
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

    tasks = Task.query.filter_by(userid=session["userid"])
    not_exists = db.session.query(User).filter_by(
        userid=session["userid"]).scalar() is None
    if not_exists:
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
