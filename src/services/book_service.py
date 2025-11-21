from fastapi import HTTPException
from src.repositories.book_repository import BookRepository
from src.db import connect_db
from asyncpg import UniqueViolationError

class BookService:

    @staticmethod
    async def add_book(book):
        pool = await connect_db()
        try:
            book_id = await BookRepository.create_book(pool, book.dict())
            return {"message": "Book added successfully", "book_id": book_id}
        except UniqueViolationError:
            raise HTTPException(status_code=400, detail="ISBN already exists")

    @staticmethod
    async def get_book(book_id: int):
        pool = await connect_db()
        row = await BookRepository.get_book_by_id(pool, book_id)
        if not row:
            raise HTTPException(status_code=404, detail="Book not found")
        return dict(row)

    @staticmethod
    async def list_books():
        pool = await connect_db()
        rows = await BookRepository.get_all_books(pool)
        return [dict(r) for r in rows]

    @staticmethod
    async def update_book(book_id: int, book):
        pool = await connect_db()
        updated_id = await BookRepository.update_book(pool, book_id, book.dict(exclude_unset=True))
        if not updated_id:
            raise HTTPException(status_code=404, detail="Book not found")
        return {"message": "Book updated successfully"}

    @staticmethod
    async def delete_book(book_id: int):
        pool = await connect_db()
        result = await BookRepository.delete_book(pool, book_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Book not found")
        return {"message": "Book deleted successfully"}
