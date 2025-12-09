import logging
from src.services.book_transaction_service import BookTransactionService

logger = logging.getLogger(__name__)

class BookTransactionController:

    @staticmethod
    async def issue_book(book_id: int, member_id: int):
        return await BookTransactionService.issue_book(book_id, member_id)

    @staticmethod
    async def return_book(transaction_id: int):
        return await BookTransactionService.return_book(transaction_id)

    @staticmethod
    async def get_issued_books():
        return await BookTransactionService.get_issued_books()

    @staticmethod
    async def get_overdue_books():
        return await BookTransactionService.get_overdue_books()

    @staticmethod
    async def get_member_issued_books(member_id: int):
        return await BookTransactionService.get_member_issued_books(member_id)

    @staticmethod
    async def create_transaction(transaction):
        return await BookTransactionService.create_transaction(transaction)

    @staticmethod
    async def get_transaction(transaction_id: int):
        return await BookTransactionService.get_transaction(transaction_id)

    @staticmethod
    async def update_transaction(transaction_id: int, transaction):
        return await BookTransactionService.update_transaction(transaction_id, transaction)

    # Get members who have a specific book issued

    @staticmethod
    async def get_book_issued_members(book_id: int):
        return await BookTransactionService.get_book_issued_members(book_id)
        pass