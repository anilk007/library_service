from datetime import datetime, timedelta, date
from typing import List, Optional
from src.models.book_transaction import BookTransactionCreate, BookTransactionUpdate, TransactionStatus
from src.config.book_library_config import BookLibraryConfig

# Sample in-memory storage for demonstration
transactions_db = []
transaction_id_counter = 1


class BookTransactionService:

    @staticmethod
    async def create_transaction(transaction_data: BookTransactionCreate):
        global transaction_id_counter

        # Convert Pydantic model to dict
        transaction_dict = transaction_data.dict()

        # If due_date is not provided, calculate it automatically
        if not transaction_dict.get('due_date') and transaction_dict.get('issue_date'):
            issue_date = transaction_dict['issue_date']
            transaction_dict['due_date'] = issue_date + timedelta(days=BookLibraryConfig.DEFAULT_DUE_DAYS)
        elif not transaction_dict.get('due_date'):
            # If neither due_date nor issue_date provided, use current date for issue_date
            transaction_dict['issue_date'] = date.today()
            transaction_dict['due_date'] = date.today() + timedelta(days=BookLibraryConfig.DEFAULT_DUE_DAYS)

        # Set default status if not provided
        if not transaction_dict.get('status'):
            transaction_dict['status'] = TransactionStatus.ISSUED

        # Add system-generated fields
        transaction_dict["transaction_id"] = transaction_id_counter
        transaction_dict["created_at"] = datetime.now()

        transactions_db.append(transaction_dict)
        transaction_id_counter += 1

        return {
            "message": "Transaction created successfully",
            "transaction": transaction_dict
        }

    @staticmethod
    async def borrow_book(book_id: int, member_id: int):
        global transaction_id_counter

        # Check if book is already borrowed and not returned
        for transaction in transactions_db:
            if (transaction["book_id"] == book_id and
                    transaction["status"] in [TransactionStatus.ISSUED, TransactionStatus.OVERDUE]):
                return {"error": "Book is already borrowed"}

        # Create new transaction with configurable due days
        issue_date = date.today()
        due_date = issue_date + timedelta(days=BookLibraryConfig.DEFAULT_DUE_DAYS)

        transaction = {
            "transaction_id": transaction_id_counter,
            "book_id": book_id,
            "member_id": member_id,
            "issue_date": issue_date,
            "due_date": due_date,
            "return_date": None,
            "status": TransactionStatus.ISSUED,
            "created_at": datetime.now()
        }

        transactions_db.append(transaction)
        transaction_id_counter += 1

        return {
            "message": "Book borrowed successfully",
            "transaction_id": transaction["transaction_id"],
            "issue_date": transaction["issue_date"],
            "due_date": transaction["due_date"],
            "due_days": BookLibraryConfig.DEFAULT_DUE_DAYS
        }

    @staticmethod
    async def return_book(transaction_id: int):
        for transaction in transactions_db:
            if (transaction["transaction_id"] == transaction_id and
                    transaction["return_date"] is None):
                transaction["return_date"] = date.today()
                transaction["status"] = TransactionStatus.RETURNED

                return {"message": "Book returned successfully"}

        return {"error": "Transaction not found or book already returned"}

    @staticmethod
    async def get_borrowed_books():
        borrowed_books = [
            t for t in transactions_db
            if t["status"] in [TransactionStatus.ISSUED, TransactionStatus.OVERDUE]
        ]
        return {"borrowed_books": borrowed_books}

    @staticmethod
    async def get_overdue_books():
        current_date = date.today()
        overdue_books = [
            t for t in transactions_db
            if t["status"] == TransactionStatus.ISSUED and t["due_date"] < current_date
        ]

        # Update status to overdue
        for book in overdue_books:
            book["status"] = TransactionStatus.OVERDUE

        return {"overdue_books": overdue_books}

    @staticmethod
    async def get_member_borrowed_books(member_id: int):
        member_books = [
            t for t in transactions_db
            if t["member_id"] == member_id and
               t["status"] in [TransactionStatus.ISSUED, TransactionStatus.OVERDUE]
        ]
        return {"member_borrowed_books": member_books}

    @staticmethod
    async def get_transaction(transaction_id: int):
        for transaction in transactions_db:
            if transaction["transaction_id"] == transaction_id:
                return {"transaction": transaction}
        return {"error": "Transaction not found"}

    @staticmethod
    async def update_transaction(transaction_id: int, update_data: BookTransactionUpdate):
        for transaction in transactions_db:
            if transaction["transaction_id"] == transaction_id:
                update_dict = update_data.dict(exclude_unset=True)
                transaction.update(update_dict)
                return {"message": "Transaction updated successfully", "transaction": transaction}
        return {"error": "Transaction not found"}