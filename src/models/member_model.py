from pydantic import BaseModel, EmailStr
from typing import Optional

class Member(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = "Active"  # Active | Inactive | Suspended
