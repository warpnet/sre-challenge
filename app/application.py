import os
import sqlite3
import logging
from flask import Flask, session, redirect, url_for, request, render_template, abort

# Setup Flask
app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Make sure there is a FLASK_SECRET
if not os.getenv("FLASK_SECRET") or os.getenv("FLASK_SECRET") == "CHANGE_THIS_KEY":
    app.logger.error("FLASK_SECRET not set correctly in the environment, check your env file")
    exit(403)

# Set the FLASK_SECRET
app.secret_key = os.environ.get('FLASK_SECRET')


def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


def is_authenticated():
    return "username" in session


def authenticate(username, password):
    connection = get_db_connection()
    users = connection.execute("SELECT * FROM users").fetchall()
    connection.close()

    for user in users:
        if user["username"] == username and user["password"] == password:
            app.logger.info(f"the user '{username}' logged in successfully with password '{password}'")
            session["username"] = username
            return True

    app.logger.warning(f"the user '{username}' failed to log in '{password}'")
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
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=os.getenv("FLASK_PORT", 5000),
        debug=os.getenv("DEBUG", False)
    )
