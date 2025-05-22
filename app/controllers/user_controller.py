from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse


class UserController:
    def __init__(self):
        self.router = APIRouter(
            prefix="/users",
            tags=["users"]
        )
        self._register_routes()
    
    def _register_routes(self):
        self.router.post("", response_model=UserResponse)(self.create_user)
        self.router.get("", response_model=List[UserResponse])(self.get_users)
        self.router.get("/{user_id}", response_model=UserResponse)(self.get_user)
        self.router.put("/{user_id}", response_model=UserResponse)(self.update_user)
        self.router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)(self.delete_user)
    
    async def create_user(self, user_data: UserCreate, db: Session = Depends(get_db)):
        service = UserService(db)
        try:
            return service.create_user(user_data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def get_users(self, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        service = UserService(db)
        return service.get_users(skip, limit)
    
    async def get_user(self, user_id: int, db: Session = Depends(get_db)):
        service = UserService(db)
        user = service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        return user
    
    async def update_user(self, user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
        service = UserService(db)
        user = service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        return user
    
    async def delete_user(self, user_id: int, db: Session = Depends(get_db)):
        service = UserService(db)
        if not service.delete_user(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        return None 