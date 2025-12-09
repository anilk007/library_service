import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter
from src.controllers.book_transaction_controller import BookTransactionController
from src.models.book_transaction import BookTransactionCreate, BookTransactionUpdate

# Create the router instance
router = APIRouter(prefix="/transactions", tags=["Book Transactions"])

@router.post("/issue")
async def issue_book(book_id: int, member_id: int):
    return await BookTransactionController.issue_book(book_id, member_id)

@router.post("/return/{transaction_id}")
async def return_book(transaction_id: int):
    return await BookTransactionController.return_book(transaction_id)

@router.get("/issued")
async def get_issued_books():
    return await BookTransactionController.get_issued_books()

@router.get("/overdue")
async def get_overdue_books():
    return await BookTransactionController.get_overdue_books()

@router.get("/member/{member_id}")
async def get_member_issued_books(member_id: int):
    return await BookTransactionController.get_member_issued_books(member_id)

@router.get("/book/{book_id}/issued-members")
async def get_book_issued_members(book_id: int):
    return await BookTransactionController.get_book_issued_members(book_id)


@router.post("")
async def create_transaction(transaction: BookTransactionCreate):
    logger.info("create_transaction of routes is called..<>..")
    print("create_transaction of routes is called")
    return await BookTransactionController.create_transaction(transaction)

@router.get("/{transaction_id}")
async def get_transaction(transaction_id: int):
    return await BookTransactionController.get_transaction(transaction_id)

@router.put("/{transaction_id}")
async def update_transaction(transaction_id: int, transaction: BookTransactionUpdate):
    return await BookTransactionController.update_transaction(transaction_id, transaction)