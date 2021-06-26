import sqlite3
from sqlite3.dbapi2 import enable_callback_tracebacks
c = sqlite3.connect('ToDo.db')


def create_table():
    # ユーザID 	 タイトル	メモ 	    日時 	   場所
    # userid     title     memo         date    place
    # char[100]	 char[50]  char[1000]  char[20] char[300]
    c.execute("drop table if exists todo;")
    c.execute("create table if not exists todo (userid varchar(100), title varchar(50), memo varchar(1000), date varchar(20), place varchar(300));")


def read():
    pass


def create(userid="None", title="None", memo="None", date="None", place="None", taskid="None"):
    exec = "insert into test values (\"" + userid + "\", \"" + title + "\", \"" \
        + memo + "\", \"" + date + "\", \"" + place + "\", \"" + taskid + "\");"
    print(exec)
    # c.execute(exec)
    pass


def delete():
    pass


if __name__ == "__main__":
    # create("a", "a", "a", "a", "a", "a")
    create()
