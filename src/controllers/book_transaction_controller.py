from src.services.book_transaction_service import BookTransactionService
from src.models.book_transaction import BookTransactionCreate, BookTransactionUpdate, BookTransactionResponse

class BookTransactionController:

    @staticmethod
    async def borrow_book(book_id: int, member_id: int):
        """Borrow a book (create a transaction)"""
        return await BookTransactionService.borrow_book(book_id, member_id)

    @staticmethod
    async def return_book(transaction_id: int):
        """Return a borrowed book"""
        return await BookTransactionService.return_book(transaction_id)

    @staticmethod
    async def get_issued_books():
        """Get all currently borrowed books"""
        return await BookTransactionService.get_borrowed_books()

    @staticmethod
    async def get_overdue_books():
        """Get all overdue books"""
        return await BookTransactionService.get_overdue_books()

    @staticmethod
    async def get_member_borrowed_books(member_id: int):
        """Get all books borrowed by a specific member"""
        return await BookTransactionService.get_member_borrowed_books(member_id)

    @staticmethod
    async def create_transaction(transaction_data: BookTransactionCreate):
        """Create a new book transaction"""
        return await BookTransactionService.create_transaction(transaction_data)

    @staticmethod
    async def get_transaction(transaction_id: int):
        """Get a specific transaction"""
        return await BookTransactionService.get_transaction(transaction_id)

    @staticmethod
    async def update_transaction(transaction_id: int, update_data: BookTransactionUpdate):
        """Update a transaction"""
        return await BookTransactionService.update_transaction(transaction_id, update_data)