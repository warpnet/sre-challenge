import sqlite3
import logging
from flask import Flask, session, redirect, url_for, request, render_template, abort


app = Flask(__name__)
app.config.from_pyfile("instance/config.py")
app.logger.setLevel(logging.INFO)


def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


def is_authenticated():
    if "username" in session:
        return True
    return False


def authenticate(username, password):
    connection = get_db_connection()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    user = connection.execute(query, (username, password)).fetchone()
    connection.close()

    if user:
        app.logger.info(f"the user '{username}' logged in successfully.")
        session["username"] = username
        return True

    app.logger.warning(f"the user '{username}' failed to log in.")
    abort(401)


@app.route("/")
def index():
    return render_template("index.html", is_authenticated=is_authenticated())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if authenticate(username, password):
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
