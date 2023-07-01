// Search book by its title and author
function search_book() {

    // Get elements of all books
    let input, book, book_title, book_author, number_of_books;

    input = document.getElementById("search_box");
    input = input.value.toLowerCase();

    book = document.getElementsByClassName("book_card");
    book_title = document.getElementsByClassName("book_title");
    book_author = document.getElementsByClassName("book_author");
    number_of_books = book.length;

    // Loop through all books, and hide those who don't match the search query
    for (i = 0; i < number_of_books; i++)
    {
        if (!book_title[i].innerHTML.toLowerCase().includes(input) && !book_author[i].innerHTML.toLowerCase().includes(input))
        {
            book[i].style.display="none";
        }
        else
        {
            book[i].style.display="";
        }
    }
};

// Show and hide elements on a page
function edit(show, hide) {

    // Get elements to show and hide
    var shows = document.getElementsByClassName(show);
    var hides = document.getElementsByClassName(hide);

    length = shows.length

    // Loop through all elements and hide / show them
    for (var i = 0; i < length; i++)
    {
        if (shows[i].style.display == "none")
        {
            shows[i].style.display = "";
            hides[i].style.display = "none";
        }
        else
        {
            hides[i].style.display = "";
            shows[i].style.display = "none";
        }
    }
};

// Error message
function error_message(message) {

    Swal.fire({
        icon: 'error',
        title: 'Oops...',
        text: message
      })  
};

// Success message
function success_message(message) {

    Swal.fire({
        icon: 'success',
        title: 'Success!',
        text: message
      })
};

// Check password
function check_new_password(page) {

    var password = document.forms[page]["password"].value;
    var confirmation = document.forms[page]["confirmation"].value;
    var length = password.length;
    var digit = false;
    var upper = false;

    if (password != confirmation)
    {
        error_message("Passwords don't match");
        return false;
    }

    for (var i = 0; i < length; i++)
    {
        var character = password[i];

        if (character >= '0' && character <= '9')
        {
            digit = true;
        }
        else if (character == character.toUpperCase())
        {
            upper = true;
        }
    }
    
    if (!(digit && upper && length > 5))
    {
        error_message("Password must contain at least 6 characters, including minimum one upper letter and one number");
        return false;
    }

    return true;
};

// Show error and success message
document.addEventListener("DOMContentLoaded", function() {
    
    var error = document.getElementById("error");
    var success = document.getElementById("success");
    
    if (error)
    {   
        error_message(error.innerHTML);
    }

    else if (success)
    {
        success_message(success.innerHTML);
    }
});
