from alayatodo import app
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash
)
import json
from flask_paginate import Pagination, get_page_args


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'" ;
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    return render_template('todo.html', todo=todo)


@app.route('/todo', defaults={'page':1}, methods=['GET'])
@app.route('/todo/', defaults={'page':1}, methods=['GET'])
@app.route('/todo/page/<int:page>', methods=['GET'])
@app.route('/todo/page/<int:page>/', methods=['GET'])
def todos(page):
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT Count(*) FROM todos")
    total = cur.fetchone()[0]
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')

    sql = "SELECT * FROM todos limit {}, {}".format(offset, per_page)
    cur = g.db.execute(sql)
    todos = cur.fetchall()

    pagination = Pagination(page=page,
                            per_page=per_page,
                            total=total,
                            record_name='todos',
                            format_total=True,
                            format_number=True,
                            css_framework='foundation'
                            )

    return render_template('todos.html', todos=todos,
                           page=page,
                           per_page=per_page,
                           pagination=pagination, )


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    error = None
    if not session.get('logged_in'):
        return redirect('/login')

    try:
        g.db.execute(
            "INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"
            % (session['user']['id'], request.form.get('description', ''))
        	)
        g.db.commit()
        error = "Insert successful!"
    except sqlite3.IntegrityError:
        error = "Unable to insert!"
    flash(error)
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    error = None
    if not session.get('logged_in'):
        return redirect('/login')
    try:
        g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
        g.db.commit()
        error = "Delete successful!"
    except sqlite3.IntegrityError:
        error = "Unable to delete!"
    flash(error)
    return redirect('/todo')


@app.route('/markcomplete/<id>', methods=['POST'])
def todo_complete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    if todo['completed'] == 0:
        g.db.execute("UPDATE todos SET completed=1 WHERE id ='%s'" % id)
    else:
        g.db.execute("UPDATE todos SET completed=0 WHERE id ='%s'" % id)

    g.db.commit()
    return redirect('/todo')


@app.route('/todo/<id>/json', methods=['POST'])
def todo_exportjson(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    with open("data_file.json", "w") as outfile:
        json.dump({'id':todo['id'], 'description':todo['description']}, outfile)

    return redirect('/todo')
