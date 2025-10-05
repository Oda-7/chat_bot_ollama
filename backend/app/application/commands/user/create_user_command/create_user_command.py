from typing import Optional
from app.domain.interfaces.repositories.user.i_user_repository import IUserRepository
from app.application.dto.user.create_user_dto import CreateUserDTO

class CreateUserCommand:
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password

class CreateUserCommandHandler:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def handle(self, command: CreateUserCommand) -> Optional[object]:
        existing_user = self.user_repository.get_user_by_username(command.username)
        if existing_user:
            raise Exception("Ce nom d'utilisateur existe déjà")

        existing_email = self.user_repository.get_user_by_email(command.email)
        if existing_email:
            raise Exception("Cette adresse email est déjà utilisée")

        user: CreateUserDTO = self.user_repository.create_user(
            username=command.username,
            email=command.email,
            password=command.password
        )
        return user