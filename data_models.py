from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'  #  Define table name

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<Author id={self.id} name='{self.name}'>"

    def __str__(self):
        return f"{self.name} (Born: {self.birth_date}, Died: {self.date_of_death})"


class Book(db.Model):
    __tablename__ = 'books'  # Define table name

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer)
    # Foreign key to the authors table
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    cover_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Book id={self.id} title='{self.title}'>"

    def __str__(self):
        return f"'{self.title}' by {self.author.name} ({self.publication_year})"