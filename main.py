from flask import Flask
from flask.globals import request, session
from flask.helpers import url_for
from flask.templating import render_template
from werkzeug.utils import redirect
from flask import flash
from flask import g
from functools import wraps
import sqlite3
import mysql.connector

mydb = mysql.connector.connect(
    host='localhost', user='flask', password='password@!@#', database='healthhack')
mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM clinic")

myresult = mycursor.fetchall()


app = Flask(__name__)


app.database = "healthhack.db"


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
# @login_required
def home():
    return render_template('welcome.html')


@app.route('/welcome')
def real_homepage():
    return render_template('welcome.html')


@app.route('/patient')
def patient():
    return render_template("patient.html")


@app.route('/Update', methods=['POST', 'GET'])
def patient_update():
    if request.method == 'POST':
        date = request.form.get('date')
        health_num = request.form.get('health_num')
        category = request.form.get('category')
        notes = request.form.get('notes')
        query = "UPDATE patient SET {} = %s, entry_date = %s WHERE health_num = %s".format(
            category)
        mycursor.execute(query, (notes, date, health_num))
        mydb.commit()
        return render_template('success.html')

    return render_template('Update.html')


@app.route('/History', methods=['POST', 'GET'])
def patient_get():
    if request.method == 'POST':
        date = request.form.get('date2')
        health_num = request.form.get('health_num2')
        category = request.form.get('category2')
        query = "SELECT {} FROM patient WHERE entry_date = %s AND health_num = %s".format(
            category)
        mycursor.execute(query, (date, health_num))
        myresult = mycursor.fetchall()
        posts = [dict(Description=row[0]) for row in myresult]
        return render_template('Medical-History-Page.html', title=category, posts=posts)

    return render_template('History.html')


@app.route('/login', methods=['POST', 'GET'])
def doctor_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        query = "SELECT * FROM physician_login WHERE email = %s AND user_password = %s"
        mycursor.execute(query, (email, password))
        myresult = mycursor.fetchall()
        if myresult != []:
            return render_template("doc_landing.html")
    return render_template("login.html")


@app.route('/doc_landing')
def landing_page():
    return render_template('doc_landing.html')


@app.route('/doc_update', methods=['POST', 'GET'])
def doc_update():
    if request.method == 'POST':
        name = request.form.get('name')
        date = request.form.get('date2')
        health_num = request.form.get('health_num')
        category = request.form.get('category')
        notes = request.form.get('notes')
        test_query = "SELECT * FROM patient WHERE health_num = %s"
        mycursor.execute(test_query, (health_num, ))
        results = mycursor.fetchall()
        if results == []:
            query = "INSERT INTO patient (patient_name, physician_id, health_num, entry_date) VALUES (%s, 1, %s, {})".format(
                date)
            mycursor.execute(query, (name, health_num))
            query = "UPDATE patient SET {} = %s, entry_date = %s WHERE health_num = %s".format(
                category)
            mycursor.execute(query, (notes, date, health_num))
        else:
            query = "UPDATE patient SET {} = %s, entry_date = %s WHERE health_num = %s".format(
                category)
            mycursor.execute(query, (notes, date, health_num))

        mydb.commit()
        return render_template('doc_success.html')

    return render_template('doc_update.html')


@app.route('/doc_success')
def doc_success():
    return render_template('doc_success.html')


@app.route('/doc_history', methods=['POST', 'GET'])
def doc_history():
    if request.method == 'POST':
        date = request.form.get('date2')
        health_num = request.form.get('health_num2')
        category = request.form.get('category')
        query = "SELECT {} FROM patient WHERE entry_date = %s AND health_num = %s".format(
            category)
        mycursor.execute(query, (date, health_num))
        myresult = mycursor.fetchall()
        posts = [dict(Description=row[0]) for row in myresult]
        return render_template('doc_history_final_page.html', title=category, posts=posts)

    return render_template('doc_history.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
