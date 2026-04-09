from pydantic import BaseModel, EmailStr

class ContactRequest(BaseModel):
    name: str
    email: str
    message: str

class ContactResponse(BaseModel):
    success: bool
    message: str
