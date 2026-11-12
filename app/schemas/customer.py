from pydantic import BaseModel,EmailStr

class CustomerCreate(BaseModel):
    name: str
    city: str
    email: EmailStr
    
class CustomerUpdate(BaseModel):
    name: str
    city: str
    email: EmailStr