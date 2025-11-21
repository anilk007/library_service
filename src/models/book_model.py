from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    publisher: Optional[str] = None
    genre: Optional[str] = None
    total_copies: int = 1
    available_copies: int = 1
