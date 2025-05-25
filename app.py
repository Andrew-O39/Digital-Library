import os
from datetime import datetime

from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from sqlalchemy import asc, or_
from dotenv import load_dotenv

from data_models import db, Author, Book

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'library.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db.init_app(app)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    success_message = None

    if request.method == 'POST':
        name = request.form['name']

        # Convert string to date object
        birth_date_str = request.form['birthdate']
        date_of_death_str = request.form['date_of_death']

        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None
        date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None

        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(new_author)
        db.session.commit()

        success_message = f"Author '{name}' added successfully!"

    return render_template('add_author.html', success_message=success_message)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    success_message = None
    authors = Author.query.all()  # Needed for the dropdown

    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']
        cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id,
            cover_url=cover_url
        )
        db.session.add(new_book)
        db.session.commit()

        success_message = f"Book '{title}' added successfully!"

    return render_template('add_book.html', authors=authors, success_message=success_message)


@app.route('/')
def home():
    sort_by = request.args.get('sort', 'title')
    query_string = request.args.get('q', '')

    # Start with a basic query joined with Author
    book_query = db.session.query(Book, Author).join(Author)

    # If there's a search term, filter it
    if query_string:
        book_query = book_query.filter(Book.title.ilike(f"%{query_string}%"))

    # Sort
    if sort_by == 'author':
        book_query = book_query.order_by(Author.name)
    else:
        book_query = book_query.order_by(Book.title)

    books = book_query.all()

    return render_template('home.html', books=books, current_sort=sort_by, query=query_string)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    # Find the book
    book = Book.query.get_or_404(book_id)
    author_id = book.author_id

    # Delete the book
    db.session.delete(book)
    db.session.commit()

    # Check if author has other books
    remaining_books = Book.query.filter_by(author_id=author_id).count()
    if remaining_books == 0:
        author = Author.query.get(author_id)
        if author:
            db.session.delete(author)
            db.session.commit()
            flash(f'Book and author "{author.name}" deleted successfully.')
        else:
            flash("Book deleted, but no matching author found.")
    else:
        flash(f'Book "{book.title}" deleted successfully.')

    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
        print("Tables created successfully.")
    app.run(debug=True)