from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import os
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import *

# Configure upload folder
UPLOAD_FOLDER = "static/upload_folder"

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies) and upload folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///shelf.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    # Forget any user_id
    session.clear()

    # Handle error message
    error = False

    if request.method == "POST":

        # Get input from user
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username does not exist
        usernames = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(usernames) > 0:
            error = "That username is already taken"

        else:
            # Generate hash of the password
            hashed_password = generate_password_hash(password)

            # Add username and hash into the database
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed_password)

            # Show success message on the next page
            message = "You are registered!"

            return render_template("login.html", success=message)
    
    return render_template("register.html", error=error)
    

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Allow user to change password"""

    # Handle error message
    error = False

    if request.method == "POST":

        # Get input from the user
        old_password = request.form.get("old_password")
        new_password = request.form.get("password")

        # Ensure proper password was submitted
        hashed_password = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
        hashed_password = hashed_password[0]["hash"]

        if not check_password_hash(hashed_password, old_password):
            error = "Wrong password"

        else:
            # Update the database
            new_password = generate_password_hash(new_password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", new_password, session["user_id"])

            # Show success message
            message = "Your password is changed!"

            return render_template("change_password.html", success=message)
    
    return render_template("change_password.html", error=error)


@app.route("/login", methods = ["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # Handle error message
    error = False

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Get input from user
        username = request.form.get("username")
        password = request.form.get("password")

        # Get their username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
       
        # Ensure given username exists
        if len(rows) != 1:
            error = "This username doesn't exist"
            return render_template("login.html", error=error)

        # Ensure right password was submitted
        hash = rows[0]["hash"]
        if not check_password_hash(hash, password):
            error = "Wrong password"

        else:
            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]
        
            # Redirect user to home page
            return redirect("/")
    
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/about")
def about():
    '''Personal page'''

    return render_template("about.html")


@app.route("/")
@login_required
def home_page():
    '''Show all the information about users library'''

    # Get number of all books
    number_of_books_library = get_number_of_books("library")
    number_of_books_wish_list = get_number_of_books("wish_list")

     # Get all information about users locations
    locations = get_locations()
    locations = get_number_of_books_at_location(locations)
    number_of_locations = len(locations)

    # Get all information about users categories
    categories = get_categories()
    categories = get_number_of_books_in_each_category(categories)
    number_of_categories = len(categories)

    return render_template(
        "home.html", categories=categories, locations=locations, number_of_books_library=number_of_books_library, 
            number_of_books_wish_list=number_of_books_wish_list, number_of_locations=number_of_locations, 
                number_of_categories=number_of_categories)


@app.route("/library")
@login_required
def library():
    ''' Show user all their books'''

    # Get all books in the library
    books = get_books("library")
    number_of_books = len(books)

    return render_template("library.html", books=books, number_of_books=number_of_books)


@app.route("/wish_list", methods=["GET", "POST"])
@login_required
def wish_list():
    '''Show user their wish list'''

    # Get all books and categories
    books = get_books("wish_list")
    number_of_books = len(books)
    categories = get_categories()
    
    # Add new book to the wish list
    if request.method == "POST":

        # Get input from the user
        title, author = request.form.get("title"), request.form.get("author")
        link, category = request.form.get("link"), request.form.get("category")
        cover = request.files["cover"]
        status = "wish_list"

        try:
            # Handle the book cover
            if not cover.filename:
                filename = "book_cover(brown).png"

            if cover.filename and allowed_file(cover.filename):
                filename = secure_filename(cover.filename)
                cover.save(os.path.join(app.root_path, app.config["UPLOAD_FOLDER"], filename))
            
            # Add book to the database
            db.execute("INSERT INTO books (title, author, link, status, cover, reader) VALUES (?, ?, ?, ?, ?, ?)", 
                    title, author, link, status, filename, session["user_id"])
        
        except UnboundLocalError:
            # Show error message
            message = "Sorry, this type of file is not supported"

            return render_template("wish_list.html", error=message)
        
        else:
            # Show success message
            message = "The book is added to your wish list"

            # Handle category
            if category:
                book_id = get_book_id(title)
                category_id = get_category_id(category)
                
                # Update database
                add_category_to_book(book_id, category_id)

            return render_template("wish_list.html", success=message, books=books, categories=categories, number_of_books=number_of_books)
    
    else:
        return render_template("wish_list.html", books=books, categories=categories, number_of_books=number_of_books)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    '''Add new book to the shelf'''

    # Get all users locations and categories
    locations = get_locations()
    categories = get_categories()

    if request.method == "POST":

        # Get input from the user
        title, author = request.form.get("title"), request.form.get("author")
        location, category = request.form.get("location"), request.form.get("category")
        cover = request.files["cover"]
                
        try:
            # Handle the book cover
            if not cover.filename:
                filename = "book_cover(brown).png"

            if cover.filename and allowed_file(cover.filename):
                filename = secure_filename(cover.filename)
                cover.save(os.path.join(app.root_path, app.config["UPLOAD_FOLDER"], filename))
            
            # Add book to the database
            db.execute("INSERT INTO books (title, author, status, cover, reader) VALUES (?, ?, ?, ?, ?)", 
                    title, author, "library", filename, session["user_id"])

        except UnboundLocalError:
            # Show error message
            message = "Sorry, this type of file is not supported"
            return render_template("add.html", error=message)
        
        else:
            # Show succes message
            message = "The book is added to your library"
            
            book_id = get_book_id(title)

            # Handle the location
            if location:
                location_id = get_location_id(location)

                # Update the database
                add_location_to_book(book_id, location_id)

            # Handle the category
            if category:
                category_id = get_category_id(category)

                # Update the database
                add_category_to_book(book_id, category_id)

            return render_template("add.html", success=message, categories=categories, locations=locations)
        
    else:
        return render_template("add.html", categories=categories, locations=locations)
    

@app.route("/book/<title>", methods=["GET", "POST"])
@login_required
def book(title):
    '''Show content of each book in the library'''

    # Get information about book
    book = get_book(title)
    book_id = book["id"]

    # Get the information about books location
    number_of_locations = len(get_locations())
    location = get_location_of_book(book_id)

    # Check if the book has a location
    if location:
        location = location["name"]
        number_of_books_at_location = get_number_of_books_at_location(location)
    
    else:
        location, number_of_books_at_location = None, None
         
    # Show books categories
    categories = get_categories_of_book(book_id)
    
    # Get number of books in each category
    categories = get_number_of_books_in_each_category(categories)
    
    # Allow to add new categories
    all_categories = get_categories()

    # Ensure categories don't repeat 
    new_categories = list()

    for one in all_categories:
        new_categories.append(one["name"])
    
    for category in categories:
        if category["name"] in new_categories:
            new_categories.remove(category["name"])
    
    # Add a new category to the book
    if request.method == "POST":

        # Get input from the user
        new_category = request.form.get("category")        
        new_category_id = get_category_id(new_category)

        # Update the database
        add_category_to_book(book_id, new_category_id)

        return redirect(f"/book/{title}")

    else:
        return render_template("book.html", book=book, title=title, categories=categories, 
                               new_categories=new_categories, location=location, 
                               number_of_locations=number_of_locations, 
                               number_of_books_at_location=number_of_books_at_location)


@app.route("/locations", methods=["GET", "POST"])
@login_required
def locations():
    '''Manage books locations'''

    # Get all users locations
    locations = get_locations()

    # Get number of locations
    number_of_locations = len(locations)

    # Get number of books at each location
    locations = get_number_of_books_at_location(locations)

    # Add new location
    if request.method == "POST":

        # Get input
        new_location = request.form.get("add_location")

        # Ensure a new location was submitted
        old_locations = list()

        for location in locations:
            old_locations.append(location["name"])
        
        if new_location in old_locations:
            error = "This location already exists"
            return render_template("locations.html", locations=locations, number_of_locations=number_of_locations, error=error)

        # Update the database
        add_new_location(new_location)

        return redirect("/locations")
    
    else:
        return render_template("locations.html", locations=locations, number_of_locations=number_of_locations)
    

@app.route("/<location>/books")
@login_required
def books_at_location(location):
    '''Show all books at the given location'''
    
    # Get all books at the location
    books = get_books_at_locaiton(location)

    return render_template("books_at_location.html", books=books, location=location)


@app.route("/delete_location/<location>")
@login_required
def delete_location(location):
    '''Allow user to delete an existing location'''

    # Get location id
    location_id = get_location_id(location)

    # Update the database
    db.execute("DELETE FROM located_books WHERE location_id = ?", location_id)
    db.execute("DELETE FROM locations WHERE id = ?", location_id)

    return redirect("/locations")


@app.route("/select_location_for_<title>", methods=["GET", "POST"])
@login_required
def select_location_for_book(title):
    '''Show the user all possible new locations for the given book'''

    # Get all possible location for the book
    all_locations = get_locations()
    number_of_locations = len(all_locations)

    if not number_of_locations:
        redirect("/locations")

    new_locations = list()
    for one in all_locations:
        new_locations.append(one["name"])
    
    # Get information about the book
    book_id = get_book_id(title)
    location = get_location_of_book(book_id)

    if location:
        location = get_location_of_book(book_id)["name"]
        new_locations.remove(location)

    # Move the book to a different location
    if request.method == "POST":

        # Get input
        new_location = request.form.get("new_location")

        # Update the database
        new_location_id = get_location_id(new_location)

        db.execute("DELETE FROM located_books WHERE book_id = ?", book_id)
        add_location_to_book(book_id, new_location_id)

        return redirect(f"/book/{title}")
    
    else:
        return render_template("select_location.html", title=title, new_locations=new_locations)


@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    '''Manage book categories'''

    # Get all users categories
    categories = get_categories()

    # Get number of categories
    number_of_categories = len(categories)

    # Get number of books in each category
    categories = get_number_of_books_in_each_category(categories)

    # Add new category
    if request.method == "POST":

        # Get input
        new_category = request.form.get("add_category")

        # Ensure a new category was submitted
        old_categories = list()

        for category in categories:
            old_categories.append(category["name"])
    
        if new_category in old_categories:
            error = "This category already exists"
            return render_template("categories.html", categories=categories, number_of_categories=number_of_categories, error=error)
        
        # Update the database
        add_new_category(new_category)
        
        return redirect("/categories")

    else:
        return render_template("categories.html", categories=categories, number_of_categories=number_of_categories)


@app.route("/books/<category>")
@login_required
def books_in_category(category):
    '''Show all books in the given category'''

    # Get all books in the category
    books = get_books_in_category(category)

    return render_template("books_in_category.html", books=books, category=category)


@app.route("/delete_category/<category>")
@login_required
def delete_category(category):
    '''Allow user to delete an existing category'''

    # Get category id
    category_id = get_category_id(category)
  
    # Update the database
    db.execute("DELETE FROM sorted_books WHERE category_id = ?", category_id)
    db.execute("DELETE FROM categories WHERE id = ?", category_id)
    
    return redirect("/categories")


@app.route("/delete_<title>/<category>")
@login_required
def delete_book_from_category(title, category):
    '''Allow user to delete a book from an existing category'''

    # Get book id and category id
    book_id = get_book_id(title)
    category_id = get_category_id(category)

    # Update the database
    db.execute("DELETE FROM sorted_books WHERE category_id = ? AND book_id = ?", category_id, book_id)

    return redirect(f"/book/{title}")


@app.route("/delete/<title>")
@login_required
def delete_book(title):
    '''Delete a book from the library'''

    # Get book id and its status
    book_id = get_book_id(title)
    status = get_status_of_book(book_id)

    # Update the database
    db.execute("DELETE FROM sorted_books WHERE book_id = ?", book_id)
    db.execute("DELETE FROM located_books WHERE book_id = ?", book_id)
    db.execute("DELETE FROM books WHERE id = ?", book_id)

    # Return to the previous page
    if status == "library":

        return redirect("/library")
    
    else:
        return redirect("/wish_list")


@app.route("/buy/<title>")
@login_required
def buy(title):
    '''Transfer book from wish list to the library'''

    # Update the database
    book_id = get_book_id(title)
    status = "library"

    db.execute("UPDATE books SET status = ? WHERE id = ?", status, book_id)

    return redirect(f"/book/{title}")


if __name__ == "__main__":
    app.run(debug=True)
