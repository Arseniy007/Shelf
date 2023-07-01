from flask import redirect, render_template, session
from functools import wraps
from cs50 import SQL


ALLOWED_EXTENSIONS = set(["jpg", "jpeg", "png"])


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///shelf.db")


def login_required(f):
    """Decorate routes to require login."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_book(title):
    '''Get all information about book by its title'''

    return db.execute("SELECT id, author, cover, status FROM books WHERE title = ? AND reader = ?", title, session["user_id"])[0]


def get_book_id(title):
    '''Get book id by its title'''

    return db.execute("SELECT id FROM books WHERE title = ? AND reader = ?", title, session["user_id"])[0]["id"]


def get_books(status):
    '''Get all users books in library'''

    books = db.execute("SELECT id, title, author, cover, link FROM books WHERE status = ? AND reader = ? ORDER BY id DESC", 
                       status, session["user_id"])
      
    return books


def get_status_of_book(book_id):
    '''Get status (library / wish list) of the given book'''

    return db.execute("SELECT status FROM books WHERE id = ? AND reader = ?", book_id, session["user_id"])[0]["status"]


def get_number_of_books(status):
    '''Get all users books in the library'''

    return db.execute("SELECT COUNT(id) FROM books WHERE status = ? AND reader = ?", status, session["user_id"])[0]["COUNT(id)"]


def get_locations():
    '''Get all users location'''
    
    return db.execute("SELECT name FROM locations WHERE reader = ?", session["user_id"])


def get_location_id(location):
    '''Get id of a location by its name'''

    return db.execute("SELECT id FROM locations WHERE name = ? AND reader = ?", location, session["user_id"])[0]["id"]


def add_new_location(location):
    '''Add new location'''

    return db.execute("INSERT INTO locations (name, reader) VALUES (?, ?)", location, session["user_id"])


def get_location_of_book(book_id):
    '''Get location of a given book by its id'''

    try:
        location = db.execute("SELECT id, name FROM locations JOIN located_books ON locations.id = located_books.location_id WHERE book_id = ?",
                book_id)[0]
        
    except IndexError:
        location = None
    
    return location


def get_books_at_locaiton(location):
    '''Get all users books at the given location'''

    location_id = get_location_id(location)

    books = db.execute(
        "SELECT id, title, author, cover FROM books JOIN located_books ON books.id = located_books.book_id WHERE location_id = ?", 
        location_id)
    
    return books


def add_location_to_book(book_id, location_id):
    '''Add new location to the book'''

    return db.execute("INSERT INTO located_books (book_id, location_id) VALUES (?, ?)", book_id, location_id)


def get_number_of_books_at_location(location):

    # If there are multiple locations
    if type(location) == list:

        # Count all books
        for one in location:

            location_id = get_location_id(one["name"])
            
            number_of_books = db.execute(
                "SELECT COUNT(book_id) FROM located_books JOIN books ON located_books.book_id = books.id WHERE location_id = ?",
                    location_id)[0]["COUNT(book_id)"]
            
            one["count"] = number_of_books
        
        return location
    
    # If there is only one given
    else:

        location_id = get_location_id(location)

        # Count all books
        number_of_books = db.execute(
                "SELECT COUNT(book_id) FROM located_books JOIN books ON located_books.book_id = books.id WHERE location_id = ?",
                    location_id)[0]["COUNT(book_id)"]
        
        return number_of_books


def get_categories():
    '''Get all users categories'''

    return db.execute("SELECT name FROM categories WHERE reader = ?", session["user_id"])


def get_category_id(category):
    '''Get id of a locaiton by its name'''
    
    return db.execute("SELECT id FROM categories WHERE name = ? AND reader = ?", category, session["user_id"])[0]["id"]
  

def add_new_category(category):
    '''Add new category'''

    return db.execute("INSERT INTO categories (name, reader) VALUES (?, ?)", category, session["user_id"])


def get_categories_of_book(book_id):
    '''Get all the categories of the given book'''

    categories = db.execute(
        "SELECT name FROM categories JOIN sorted_books ON categories.id = sorted_books.category_id WHERE book_id = ?", book_id)
    
    return categories


def get_books_in_category(category):
    """Get all users books in the given category"""

    category_id = get_category_id(category)
    status = "library"

    books = db.execute(
        "SELECT id, title, author, cover FROM books JOIN sorted_books ON books.id = sorted_books.book_id WHERE category_id = ? AND status = ?", 
        category_id, status)
    
    return books


def add_category_to_book(book_id, category_id, ):
    '''Add new category to the book'''

    return db.execute("INSERT INTO sorted_books (book_id, category_id) VALUES (?, ?)", book_id, category_id)


def get_number_of_books_in_each_category(categories):

    # Show books only in the library
    status = "library"

    # Count all books
    for category in categories:

        category_id = db.execute("SELECT id FROM categories WHERE name = ? AND reader = ?", 
                                    category["name"], session["user_id"])[0]["id"]
        
        number_of_books = db.execute(
            "SELECT COUNT(book_id) FROM sorted_books JOIN books ON sorted_books.book_id = books.id WHERE category_id = ? AND status = ?", 
                                        category_id, status)[0]["COUNT(book_id)"]
        
        category["count"] = number_of_books
    
    return categories 
