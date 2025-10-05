from typing import Optional
from app.domain.interfaces.repositories.user.i_user_repository import IUserRepository

class LoginUserQuery:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

class LoginUserQueryHandler:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def handle(self, query: LoginUserQuery) -> Optional[object]:
        user = self.user_repository.authenticate_user(query.username, query.password)
        return user