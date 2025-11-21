from fastapi import APIRouter
from src.models.book_model import Book
from src.controllers.book_controller import BookController

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("")
async def create_book(book: Book):
    return await BookController.create_book(book)

@router.get("/{book_id}")
async def get_book(book_id: int):
    return await BookController.get_book(book_id)

@router.get("")
async def list_books():
    return await BookController.list_books()

@router.put("/{book_id}")
async def update_book(book_id: int, book: Book):
    return await BookController.update_book(book_id, book)

@router.delete("/{book_id}")
async def delete_book(book_id: int):
    return await BookController.delete_book(book_id)
