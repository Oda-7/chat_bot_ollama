from pydantic import BaseModel

class CreateUserDTO(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool