# flask todo application

googleでログインするToDoリスト  
client_id, client_secretはGoogle Cloud Platformにて生成してください。  
passwordにはgoogleアカウントのパスワードを入れてください。
Id Tokenの検証に利用しているGoogleの公開鍵を更新する機能は実装されていません。

ライブラリのインストール
- pip install Flask
- pip install Flask-SQLAlchemy
- pip install sqlalchemy
- pip install hashlib
- pip install PyJWT
- pip install cryptography

サーバの起動
- python main.py

実行確認済み環境
- python 3.8.5
- python 3.9.5
