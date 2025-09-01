from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    """
    Represents an author with optional birth and death dates.
    """
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    # Relationship to Book
    books = db.relationship('Book', back_populates='author', lazy=True, cascade='all, delete-orphan') # Optional: removes books if author is deleted

    def __repr__(self):
        return f"<Author id={self.id} name='{self.name}'>"

    def __str__(self):
        return f"{self.name} (Born: {self.birth_date}, Died: {self.date_of_death})"


class Book(db.Model):
    """
    Represents a book, which must be associated with an author.
    """
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer)
    cover_url = db.Column(db.String(255), nullable=True)

    # Foreign key to Author
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    # Relationship to Author
    author = db.relationship('Author', back_populates='books')

    def __repr__(self):
        return f"<Book id={self.id} title='{self.title}'>"

    def __str__(self):
        return f"'{self.title}' by {self.author.name} ({self.publication_year})"