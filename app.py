from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os
import webbrowser

app = Flask(__name__)

app.secret_key = "librarysecretkey"

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():

    connection = sqlite3.connect("library.db")

    cursor = connection.cursor()

    search = request.args.get("search")

    if search:

        cursor.execute(
            "SELECT * FROM books WHERE title LIKE ?",
            ('%' + search + '%',)
        )

    else:

        cursor.execute("SELECT * FROM books")

    books = cursor.fetchall()

    connection.close()

    return render_template(
        "index.html",
        books=books
    )


# REGISTER

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = sqlite3.connect("library.db")

        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO users(username, password) VALUES(?, ?)",
            (username, password)
        )

        connection.commit()

        connection.close()

        flash("Account Created Successfully 🎉")

        return redirect("/login")

    return render_template("register.html")


# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = sqlite3.connect("library.db")

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE username=? AND password=?
            """,
            (username, password)
        )

        user = cursor.fetchone()

        connection.close()

        if user:

            session["user"] = username
            session["welcome"] = True
            return redirect("/")

        else:

            flash("Invalid Username or Password ❌")

    return render_template("login.html")


# LOGOUT

@app.route("/logout")
def logout():

    session.pop("user", None)

    flash("Logged Out Successfully 👋")

    return redirect("/")


# PROFILE PAGE

@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/login")

    username = session["user"]

    connection = sqlite3.connect("library.db")

    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM books WHERE status='Borrowed'"
    )

    borrowed = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "profile.html",
        username=username,
        borrowed=borrowed
    )


# ADD BOOK

@app.route("/add", methods=["GET", "POST"])
def add_book():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]

        image = request.files["image"]

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

        connection = sqlite3.connect("library.db")

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO books(
            title,
            author,
            image,
            status,
            due_date,
            fine
            )
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                author,
                filename,
                "Available",
                None,
                0
            )
        )

        connection.commit()

        connection.close()

        flash("Book Added Successfully 📚")

        return redirect("/")

    return render_template("add_book.html")


# BORROW BOOK

@app.route("/borrow/<int:id>")
def borrow_book(id):

    due_date = (
        datetime.now() + timedelta(days=7)
    ).strftime("%Y-%m-%d")

    connection = sqlite3.connect("library.db")

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE books
        SET status='Borrowed',
        due_date=?,
        fine=0
        WHERE id=?
        """,
        (due_date, id)
    )

    connection.commit()

    connection.close()

    flash("Book Borrowed Successfully 📖")

    return redirect("/")


# RETURN BOOK

@app.route("/return/<int:id>")
def return_book(id):

    connection = sqlite3.connect("library.db")

    cursor = connection.cursor()

    cursor.execute(
        "SELECT due_date FROM books WHERE id=?",
        (id,)
    )

    result = cursor.fetchone()

    fine = 0

    if result[0]:

        due_date = datetime.strptime(
            result[0],
            "%Y-%m-%d"
        )

        today = datetime.now()

        late_days = (today - due_date).days

        if late_days > 0:

            fine = late_days * 10

    cursor.execute(
        """
        UPDATE books
        SET status='Available',
        due_date=NULL,
        fine=?
        WHERE id=?
        """,
        (fine, id)
    )

    connection.commit()

    connection.close()

    flash("Book Returned Successfully 🔥")

    return redirect("/")


# DELETE BOOK

@app.route("/delete/<int:id>")
def delete_book(id):

    if "user" not in session:
        return redirect("/login")

    connection = sqlite3.connect("library.db")

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM books WHERE id=?",
        (id,)
    )

    connection.commit()

    connection.close()

    flash("Book Deleted Successfully 🗑️")

    return redirect("/")


# EDIT BOOK

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id):

    if "user" not in session:
        return redirect("/login")

    connection = sqlite3.connect("library.db")

    cursor = connection.cursor()

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]

        cursor.execute(
            "UPDATE books SET title=?, author=? WHERE id=?",
            (title, author, id)
        )

        connection.commit()

        connection.close()

        flash("Book Updated Successfully ✏️")

        return redirect("/")

    cursor.execute(
        "SELECT * FROM books WHERE id=?",
        (id,)
    )

    book = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_book.html",
        book=book
    )


# DASHBOARD

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    connection = sqlite3.connect("library.db")

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM books WHERE status='Available'"
    )
    available_books = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM books WHERE status='Borrowed'"
    )
    borrowed_books = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        total=total_books,
        available=available_books,
        borrowed=borrowed_books
    )


if __name__ == "__main__":

    webbrowser.open("http://127.0.0.1:5000")

    app.run(debug=False)