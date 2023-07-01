# Shelf
#### https://youtu.be/sn6cG6evO10
#### Description:
"Shelf" is a final project for the "CS50's Introduction to Computer Science" course, which was made using Flask, SQL, JavaScript and of course some bit of HTML and CSS.

It is meant for people who want to have a digital version of their own library. With "Shelf" you can gather all your books in one place and organize them by creating different locations and categories. "Shelf" makes it easy to keep track of every book you have, as well as organizing a wish list of all the books you are looking for to buy.

Here is a quick description of things you can do with Shelf:
Adding a new book to the library (you can choose additionally a location and a category for the book, as well as uploading the book's cover); managing your locations and categories (adding and deleting them); searching by title or author of any particular book in the library; adding a new book to the wish list; searching by title or author any particular book in the wish list, etc.

#### Technical details:

- **"app.py"** is a file, where all the main backend logic is described (*Flask*). It has 21 function.

- **"helpers.py"** is a secondary python file with 22 auxiliary functions. Almost all of them consist of SQL queries. There are put there in order to keep the Flask-file as clean of SQL as possible.

- **shelf.db** is a *SQL* database with 6 tables inside: "users", "books", "categories", "locations", "sorted_books", "located_books".

- All 15 *HTML* files are stored in **templates** folder.

- **static** folder provides:

1. **scrpt.js** *JavaScript* file with 6 functions.

2. **styles.css** *CSS* file.

3. **pictures** folder with pictures, which "Shelf" uses.

4. **upload_folder** - a special folder that saves all pictures (either .png, .jpeg, or .jpg) user uploads.