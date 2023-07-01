# Shelf
#### https://youtu.be/sn6cG6evO10
#### Description:
"Shelf" is a final project for the "CS50's Introduction to Computer Science" course, which was made using Flask, SQL, JavaScript and of course some bit of HTML and CSS.

It is meant for people who want to have a digital version of their own library. With "Shelf" you can gather all your books in one place and organize them by creating different locations and categories. "Shelf" makes it easy to keep track of every book you have, as well as organizing a wish list of all the books you are looking for to buy.

#### Technical details:

- **"app.py"** is a file, where all the main backend logic is described (*Flask*).

- **"helpers.py"** is a secondary python file with auxiliary functions. Almost all of them consist of SQL queries. There are put there in order to keep the Flask-file as clean of SQL as possible.

- **shelf.db** is a *SQL* database with 6 tables inside: "users", "books", "categories", "locations", "sorted_books", "located_books".

- All *HTML* files are stored in **templates** folder.

- **static** folder provides:

1. **scrpt.js** *JavaScript* file with 6 functions.

2. **styles.css** *CSS* file.

3. **pictures** folder with pictures, which "Shelf" uses.

4. **upload_folder** - a special folder that saves all pictures (either .png, .jpeg, or .jpg) user uploads.