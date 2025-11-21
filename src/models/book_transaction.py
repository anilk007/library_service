from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, validator
from enum import Enum

class TransactionStatus(str, Enum):
    ISSUED = "Issued"
    RETURNED = "Returned"
    OVERDUE = "Overdue"

class BookTransactionBase(BaseModel):
    book_id: int
    member_id: int
    issue_date: Optional[date] = None
    due_date: Optional[date] = None  # ← Make this optional
    return_date: Optional[date] = None
    status: Optional[TransactionStatus] = TransactionStatus.ISSUED

    @validator('due_date')
    def validate_due_date(cls, v, values):
        if v and 'issue_date' in values and values['issue_date']:
            if v <= values['issue_date']:
                raise ValueError('Due date must be after issue date')
        return v

    @validator('return_date')
    def validate_return_date(cls, v, values):
        if v and 'issue_date' in values and values['issue_date']:
            if v < values['issue_date']:
                raise ValueError('Return date cannot be before issue date')
        return v

class BookTransactionCreate(BookTransactionBase):
    # All fields are inherited from BookTransactionBase
    # due_date is now optional
    pass

class BookTransactionUpdate(BaseModel):
    return_date: Optional[date] = None
    status: Optional[TransactionStatus] = None

class BookTransactionInDB(BookTransactionBase):
    transaction_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class BookTransactionResponse(BookTransactionInDB):
    pass