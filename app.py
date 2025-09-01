# Standard library
import os
from datetime import datetime

# Third-party packages
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from sqlalchemy import asc, or_
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Local application imports
from data_models import db, Author, Book

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# Set up database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db.init_app(app)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Handle the creation of a new author.
    GET: Render the add_author form.
    POST: Validate form data, handle date and DB errors, and insert the author into the database.
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        birth_date_str = request.form.get('birthdate', '')
        date_of_death_str = request.form.get('date_of_death', '')

        if not name:
            flash('Author name is required.')
            return redirect(url_for('add_author'))

        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None
            date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None

            new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
            db.session.add(new_author)
            db.session.commit()
            flash(f'Author "{name}" added successfully.')

        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
        except Exception as e:
            db.session.rollback()
            flash("Error adding author.")
        return redirect(url_for('home'))

    return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Handle form for adding a new book.
    GET: Render the add_book form.
    POST: Validate form data, fetch cover image (if applicable), and save book to the database.
    """
    authors = Author.query.order_by(Author.name).all()

    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        if not (isbn and title and author_id):
            flash("ISBN, title, and author are required.")
            return redirect(url_for('add_book'))

        try:
            cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
            new_book = Book(
                title=title,
                isbn=isbn,
                publication_year=int(publication_year) if publication_year else None,
                author_id=int(author_id),
                cover_url=cover_url
            )
            db.session.add(new_book)
            db.session.commit()
            flash(f'Book "{title}" added successfully.')

        except Exception:
            db.session.rollback()
            flash("Error adding book.")
        return redirect(url_for('home'))

    return render_template('add_book.html', authors=authors)

@app.route('/')
def home():
    """
    Display all books with optional search and sorting.
    Supports sorting by title or author, and searching by book title or author name.
    """
    sort_by = request.args.get('sort', 'title')
    query_string = request.args.get('q', '')

    book_query = Book.query.options(joinedload(Book.author))

    if query_string:
        book_query = book_query.join(Book.author).filter(
            or_(
                Book.title.ilike(f'%{query_string}%'),
                Author.name.ilike(f'%{query_string}%')
            )
        )

    if sort_by == 'author':
        book_query = book_query.join(Book.author).order_by(Author.name)
    else:
        book_query = book_query.order_by(Book.title)

    books = book_query.all()
    return render_template('home.html', books=books, current_sort=sort_by, query=query_string)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    Delete a book (and possibly its author if they have no other books).
    Redirects to home page with a success message after deletion.
    """
    # Find the book
    try:
        book = Book.query.get_or_404(book_id)
        author = book.author

        db.session.delete(book)
        db.session.commit()

        # Check if the author has other books
        if not author.books:
            db.session.delete(author)
            db.session.commit()
            flash(f'Book and author "{author.name}" deleted successfully.')
        else:
            flash(f'Book "{book.title}" deleted successfully.')

    except Exception:
        db.session.rollback()
        flash("Error deleting book.")
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)