from flask import Flask, request, Markup, abort
import database

app = Flask(__name__)


@app.route('/')
def index():
    html = '''
    <form action="/test">
        <p><label>test: </label>
        <input type="text" name="userid" value="default">
        <button type="submit" formmethod="get">GET</button>
        <button type="submit" formmethod="post">POST</button></p>
    </form>
    <button type=“button” onclick="location.href='/task_create'">task_create</button>
    '''
    return Markup(html)


@app.route('/task_create')
def task_create():
    html = '''
    <form action="/test">
        <p><label>userid: </label>
        <input type="text" name="userid" value="default">
        <p><label>title: </label>
        <input type="text" name="title" value="default">
        <p><label>memo: </label>
        <input type="text" name="memo" value="default">
        <p><label>date: </label>
        <input type="text" name="date" value="default">
        <p><label>place: </label>
        <input type="text" name="place" value="default">
        <button type="submit" formmethod="get">GET</button>
        <button type="submit" formmethod="post">POST</button></p>
    </form>
    '''
    return Markup(html)


@app.route('/test', methods=['GET', 'POST'])
def test():
    taskid = "0"
    try:
        if request.method == 'GET':
            userid = request.args.get('userid', '')
            title = request.args.get('title', '')
            memo = request.args.get('memo', '')
            date = request.args.get('date', '')
            place = request.args.get('place', '')
            taskid = taskid
            database.create(userid, title, memo, date, place, taskid)
            html = f"""
            <p>userid: {userid}</p>
            <p>title: {title}</p>
            <p>memo: {memo}</p>
            <p>date: {date}</p>
            <p>place: {place}</p>
            <p>taskid: {taskid}</p> 
            """
            return Markup(html)

        elif request.method == 'POST':
            userid = request.form['userid']
            title = request.form['title']
            html = f"""
            <p>userid: {userid}</p>
            <p>title: {title}</p>
            """
            return Markup(html)

        else:
            return abort(400)
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(debug=True)
    database.create_table()
