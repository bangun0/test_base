from typing import List, Optional
from sqlalchemy.orm import Session
import hashlib

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
    
    def _hash_password(self, password: str) -> str:
        """비밀번호를 해시화합니다."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """새로운 사용자를 생성합니다."""
        hashed_password = self._hash_password(user_data.password)
        user = self.repository.create(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        return UserResponse.model_validate(user)
    
    def get_user(self, user_id: int) -> Optional[UserResponse]:
        """ID로 사용자를 조회합니다."""
        user = self.repository.get_by_id(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """모든 사용자를 조회합니다."""
        users = self.repository.get_all(skip, limit)
        return [UserResponse.model_validate(user) for user in users]
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """사용자 정보를 업데이트합니다."""
        update_data = user_data.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = self._hash_password(update_data.pop("password"))
        
        user = self.repository.update(user_id, **update_data)
        if not user:
            return None
        return UserResponse.model_validate(user)
    
    def delete_user(self, user_id: int) -> bool:
        """사용자를 삭제합니다."""
        return self.repository.delete(user_id) 