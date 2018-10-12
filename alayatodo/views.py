from alayatodo import app, db
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash
)
import json
from flask_paginate import Pagination, get_page_args, get_page_parameter
from alayatodo.models import User, Todo, object_as_dict
from sqlalchemy import exc
import re


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

    user = object_as_dict(User.query.filter_by(username=username).filter_by(password=password).first())
    if user:
        session['user'] = user
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
    todo = Todo.query.filter_by(id=id).first()

    return render_template('todo.html', todo=todo)


@app.route('/todo', defaults={'page':1}, methods=['GET'])
@app.route('/todo/', defaults={'page':1}, methods=['GET'])
@app.route('/todo/page/<int:page>', methods=['GET'])
@app.route('/todo/page/<int:page>/', methods=['GET'])
def todos(page):
    if not session.get('logged_in'):
        return redirect('/login')
    total = Todo.query.count()
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')

    todos = Todo.query.limit(per_page).offset(offset).all()

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
                           pagination=pagination)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    error = None
    url = ''
    r = request
    base_url = r.base_url
    referrer = r.referrer

    url = re.sub(base_url, '', referrer)

    if not session.get('logged_in'):
        return redirect('/login')
    try:
        userid = session['user']['id']
        descr = request.form.get('description', '')

        mytodo = Todo(userid, descr, 0)
        db.session.add(mytodo)
        db.session.commit()
        error = "Insert successful!"
    except exc.SQLAlchemyError:
        print 'sql error'
        error = "Unable to insert!"
    flash(error)
    return redirect('/todo/'+url)


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    error = None
    url = ''
    r = request
    referrer = r.referrer

    pos = referrer.find('page')
    url = referrer[pos::]

    if not session.get('logged_in'):
        return redirect('/login')
    try:
        mytodo = Todo.query.filter_by(id=id).first()
        db.session.delete(mytodo)
        db.session.commit()
        error = "Delete successful!"
    except sqlite3.IntegrityError:
        error = "Unable to delete!"
    flash(error)
    return redirect('/todo/' + url)


@app.route('/markcomplete/<id>', methods=['POST'])
def todo_complete(id):
    url = ''
    r = request
    referrer = r.referrer

    pos = referrer.find('page')
    url = referrer[pos::]

    if not session.get('logged_in'):
        return redirect('/login')
    mytodo = Todo.query.filter_by(id=id).first()
    if mytodo.completed == 1:
        mytodo.completed = 0
    else:
        mytodo.completed = 1
    db.session.commit()
    return redirect('/todo/' + url)


@app.route('/todo/<id>/json', methods=['POST'])
def todo_exportjson(id):
    url = ''
    r = request
    referrer = r.referrer

    pos = referrer.find('page')
    url = referrer[pos::]

    mytodo = Todo.query.filter_by(id=id).first()
    with open("data_file.json", "w") as outfile:
        json.dump({'id':mytodo.id, 'description':mytodo.description}, outfile)

    return redirect('/todo/' + url)
