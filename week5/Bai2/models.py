from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship


db = SQLAlchemy()

class BookAuthor(db.Model):
    __tablename__ = "book_author"

    book_id: Mapped[int] = mapped_column(
        db.ForeignKey("books.id"), primary_key=True
    )
    author_id: Mapped[int] = mapped_column(
        db.ForeignKey("authors.id"), primary_key=True
    )


class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    slug: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)

    books: Mapped[list[Book]] = relationship(back_populates="category")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug}


class Author(db.Model):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(150), nullable=False)
    bio: Mapped[str | None] = mapped_column(db.Text, nullable=True)

    books: Mapped[list[Book]] = relationship(
        secondary="book_author", back_populates="authors"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio,
            "book_ids": sorted(book.id for book in self.books),
        }


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(200), nullable=False)
    isbn: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)
    price_vnd: Mapped[int] = mapped_column(db.Integer, nullable=False)
    stock: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)
    category_id: Mapped[int] = mapped_column(
        db.ForeignKey("categories.id"), nullable=False
    )

    category: Mapped[Category] = relationship(back_populates="books")
    authors: Mapped[list[Author]] = relationship(
        secondary="book_author", back_populates="books"
    )
    reviews: Mapped[list[Review]] = relationship(back_populates="book")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "isbn": self.isbn,
            "price_vnd": self.price_vnd,
            "stock": self.stock,
            "category_id": self.category_id,
            "genre": self.category.slug,
            "author_ids": sorted(author.id for author in self.authors),
        }


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(db.String(150), nullable=False)

    reviews: Mapped[list[Review]] = relationship(back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
        }


class Review(db.Model):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(db.Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    book_id: Mapped[int] = mapped_column(db.ForeignKey("books.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)

    book: Mapped[Book] = relationship(back_populates="reviews")
    user: Mapped[User] = relationship(back_populates="reviews")

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "comment": self.comment,
            "book_id": self.book_id,
            "user_id": self.user_id,
        }
