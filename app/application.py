import os
import sqlite3
import logging
import requests

from flask import Flask, session, redirect, url_for, request, render_template, abort
from forms import LoginForm

# Setup Flask
app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

# Make sure there is a FLASK_SECRET
if not os.getenv("FLASK_SECRET") or os.getenv("FLASK_SECRET") == "CHANGE_THIS_KEY":
    app.logger.error("FLASK_SECRET not set correctly in the environment, check your env file")
    exit(503)

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
    users = connection.execute("SELECT password FROM users WHERE username = ?", (username,)).fetchall()
    connection.close()

    if len(users) == 0 or len(users) > 1:
        app.logger.warning(f"the user '{username}' failed to log in")
        abort(401)

    if users[0]["password"] == password:
        app.logger.info(f"the user '{username}' logged in successfully")
        session["username"] = username
        return True

    app.logger.warning(f"the user '{username}' failed to log in")
    abort(401)


def validate_captcha(remote_ip=None, captcha_response=None):
    res = requests.post(os.getenv("CAPTCHA_API_SERVER"), data={
        "secret": os.getenv("CAPTCHA_PRIVATE_KEY"),
        "response": captcha_response or request.form.get('cf-turnstile-response'),
        "remoteip": remote_ip or request.environ.get('REMOTE_ADDR')
    })
    if res.status_code != 200:
        return False
    if res.json().get("success"):
        return True
    return False


@app.route("/")
def index():
    return render_template("index.html", is_authenticated=is_authenticated())


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if validate_captcha():
            if authenticate(form.username.data, form.password.data):
                return redirect(url_for("index"))
    return render_template("login.html", form=form, captcha={
        "site_key": os.getenv("CAPTCHA_SITE_KEY"),
        "captcha_js_url": os.getenv("CAPTCHA_JS_URL")
    })


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=os.getenv("FLASK_PORT", 5000),
        debug=os.getenv("DEBUG", False),
    )
