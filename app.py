
import os
from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306))
    )

@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notices ORDER BY date_posted DESC")
    notices = cursor.fetchall()
    return render_template("index.html", notices=notices)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"]=="admin" and request.form["password"]=="admin":
            session["user"]="admin"
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notices ORDER BY date_posted DESC")
    notices = cursor.fetchall()
    return render_template("dashboard.html", notices=notices)

@app.route("/add", methods=["GET","POST"])
def add():
    if "user" not in session:
        return redirect("/login")
    if request.method=="POST":
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO notices (title,content,category,expiry_date) VALUES (%s,%s,%s,%s)",
            (request.form["title"], request.form["content"], request.form["category"], request.form["expiry"])
        )
        db.commit()
        return redirect("/dashboard")
    return render_template("add.html")

@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session:
        return redirect("/login")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM notices WHERE id=%s",(id,))
    db.commit()
    return redirect("/dashboard")

@app.route('/public-add', methods=['GET', 'POST'])
def public_add():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO notices (title, content, category, expiry_date) VALUES (%s,%s,%s,%s)",
            (request.form['title'], request.form['content'], request.form['category'], request.form['expiry'])
        )
        db.commit()

        return redirect('/')

    return render_template('public_add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        cursor.execute(
            "UPDATE notices SET title=%s, content=%s, category=%s, expiry_date=%s WHERE id=%s",
            (
                request.form['title'],
                request.form['content'],
                request.form['category'],
                request.form['expiry'],
                id
            )
        )
        db.commit()
        return redirect('/dashboard')

    cursor.execute("SELECT * FROM notices WHERE id=%s", (id,))
    notice = cursor.fetchone()

    return render_template('edit.html', notice=notice)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
