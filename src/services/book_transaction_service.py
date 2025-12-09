import logging
from datetime import datetime, timedelta, date
from src.db import connect_db
from src.config.book_library_config import BookLibraryConfig
from src.models.book_transaction import BookTransactionCreate, BookTransactionUpdate, TransactionStatus
from src.repositories.book_transaction_repository import BookTransactionRepository

logger = logging.getLogger(__name__)

class BookTransactionService:

    @staticmethod
    async def create_transaction(transaction_data: BookTransactionCreate):
        logger.info("create_transaction of service is called<><>")

        transaction_dict = transaction_data.dict()

        if not transaction_dict.get('due_date') and transaction_dict.get('issue_date'):
            issue_date = transaction_dict['issue_date']
            transaction_dict['due_date'] = issue_date + timedelta(days=BookLibraryConfig.DEFAULT_DUE_DAYS)
        elif not transaction_dict.get('due_date'):
            transaction_dict['issue_date'] = date.today()
            transaction_dict['due_date'] = date.today() + timedelta(days=BookLibraryConfig.DEFAULT_DUE_DAYS)

        if not transaction_dict.get('status'):
            transaction_dict['status'] = TransactionStatus.ISSUED

        pool = await connect_db()
        try:
            result = await BookTransactionRepository.create_transaction(pool, transaction_dict)
            if result:
                return {
                    "message": "Transaction created successfully.<>..",
                    "transaction": result
                }
            else:
                return {"error": "Failed to create transaction"}
        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            return {"error": f"Database error: {str(e)}"}

    @staticmethod
    async def issue_book(book_id: int, member_id: int):
        pool = await connect_db()

        try:
            is_available = await BookTransactionRepository.is_book_available(pool, book_id)
            if not is_available:
                return {"error": "Book is already issued"}

            issue_date = date.today()
            due_date = issue_date + timedelta(days=BookLibraryConfig.DEFAULT_DUE_DAYS)

            transaction_data = {
                "book_id": book_id,
                "member_id": member_id,
                "issue_date": issue_date,
                "due_date": due_date,
                "return_date": None,
                "status": TransactionStatus.ISSUED
            }

            result = await BookTransactionRepository.create_transaction(pool, transaction_data)

            if result:
                return {
                    "message": "Book issued successfully",
                    "transaction_id": result["transaction_id"],
                    "issue_date": result["issue_date"],
                    "due_date": result["due_date"],
                    "due_days": BookLibraryConfig.DEFAULT_DUE_DAYS
                }
            else:
                return {"error": "Failed to issue book"}

        except Exception as e:
            logger.error(f"Error issuing book: {str(e)}")
            return {"error": f"Database error: {str(e)}"}

    @staticmethod
    async def return_book(transaction_id: int):
        pool = await connect_db()

        try:
            transaction = await BookTransactionRepository.get_transaction_by_id(pool, transaction_id)
            if not transaction:
                return {"error": "Transaction not found"}

            if transaction.get('return_date') is not None:
                return {"error": "Book already returned"}

            result = await BookTransactionRepository.mark_as_returned(pool, transaction_id)

            if result:
                return {"message": "Book returned successfully"}
            else:
                return {"error": "Failed to return book"}

        except Exception as e:
            logger.error(f"Error returning book: {str(e)}")
            return {"error": f"Database error: {str(e)}"}

    @staticmethod
    async def get_issued_books():
        pool = await connect_db()

        try:
            active_transactions = await BookTransactionRepository.get_active_transactions(pool)
            return {"issued_books": active_transactions}
        except Exception as e:
            logger.error(f"Error getting issued books: {str(e)}")
            return {"error": f"Database error: {str(e)}"}

    @staticmethod
    async def get_overdue_books():
        pool = await connect_db()

        try:
            await BookTransactionRepository.update_overdue_status(pool)
            overdue_transactions = await BookTransactionRepository.get_overdue_transactions(pool)
            return {"overdue_books": overdue_transactions}
        except Exception as e:
            logger.error(f"Error getting overdue books: {str(e)}")
            return {"error": f"Database error: {str(e)}"}

    @staticmethod
    async def get_member_issued_books(member_id: int):
        pool = await connect_db()

        try:
            member_transactions = await BookTransactionRepository.get_transactions_by_member(pool, member_id)

            active_books = [
                t for t in member_transactions
                if t["status"] in [TransactionStatus.ISSUED, TransactionStatus.OVERDUE]
            ]

            return {"member_issued_books": active_books}
        except Exception as e:
            logger.error(f"Error getting member issued books: {str(e)}")
            return {"error": f"Database error: {str(e)}"}

    @staticmethod
    async def get_transaction(transaction_id: int):
        pool = await connect_db()

        try:
            transaction = await BookTransactionRepository.get_transaction_by_id(pool, transaction_id)
            if transaction:
                return {"transaction": transaction}
            return {"error": "Transaction not found"}
        except Exception as e:
            logger.error(f"Error getting transaction: {str(e)}")
            return {"error": f"Database error: {str(e)}"}

    @staticmethod
    async def update_transaction(transaction_id: int, update_data: BookTransactionUpdate):
        pool = await connect_db()

        try:
            update_dict = update_data.dict(exclude_unset=True)
            result = await BookTransactionRepository.update_transaction(pool, transaction_id, update_dict)

            if result:
                return {"message": "Transaction updated successfully", "transaction": result}
            return {"error": "Transaction not found"}
        except Exception as e:
            logger.error(f"Error updating transaction: {str(e)}")
            return {"error": f"Database error: {str(e)}"}
