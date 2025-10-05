from typing import Optional
from app.domain.interfaces.repositories.user.i_user_repository import IUserRepository


class MeUserQuery:
    def __init__(self, user_id:str):
        self.user_id = user_id

class MeUserQueryHandler:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def handle(self, query: MeUserQuery) -> Optional[object] | None:
        user = self.user_repository.get_user_by_id(query.user_id)
        if not user:
            return None
        
        return user