from src.services.book_service import BookService
from src.models.book_model import Book

class BookController:

    @staticmethod
    async def create_book(book: Book):
        return await BookService.add_book(book)

    @staticmethod
    async def get_book(book_id: int):
        return await BookService.get_book(book_id)

    @staticmethod
    async def list_books():
        return await BookService.list_books()

    @staticmethod
    async def update_book(book_id: int, book: Book):
        return await BookService.update_book(book_id, book)

    @staticmethod
    async def delete_book(book_id: int):
        return await BookService.delete_book(book_id)
