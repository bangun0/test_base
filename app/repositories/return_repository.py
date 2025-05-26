from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid

from app.models.return_delivery import ReturnDelivery, ReturnTracking


class ReturnRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, return_data: dict) -> ReturnDelivery:
        return_data["return_invoice_number"] = self._generate_return_invoice_number()
        return_delivery = ReturnDelivery(**return_data)
        self.db.add(return_delivery)
        try:
            self.db.commit()
            self.db.refresh(return_delivery)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("반품 등록 중 오류가 발생했습니다.")
        return return_delivery

    def create_multiple(self, returns_data: List[dict]) -> List[ReturnDelivery]:
        returns = []
        for return_data in returns_data:
            return_data["return_invoice_number"] = self._generate_return_invoice_number()
            return_delivery = ReturnDelivery(**return_data)
            returns.append(return_delivery)
            self.db.add(return_delivery)
        
        try:
            self.db.commit()
            for return_delivery in returns:
                self.db.refresh(return_delivery)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("반품 목록 등록 중 오류가 발생했습니다.")
        return returns

    def get_by_return_invoice_number(self, return_invoice_number: str) -> Optional[ReturnDelivery]:
        return self.db.query(ReturnDelivery).filter(
            ReturnDelivery.return_invoice_number == return_invoice_number
        ).first()

    def get_by_return_invoice_numbers(self, return_invoice_numbers: List[str]) -> List[ReturnDelivery]:
        return self.db.query(ReturnDelivery).filter(
            ReturnDelivery.return_invoice_number.in_(return_invoice_numbers)
        ).all()

    def get_by_original_invoice_number(self, original_invoice_number: str) -> List[ReturnDelivery]:
        return self.db.query(ReturnDelivery).filter(
            ReturnDelivery.original_invoice_number == original_invoice_number
        ).all()

    def update_status(self, return_invoice_number: str, status: str, **kwargs) -> Optional[ReturnDelivery]:
        return_delivery = self.get_by_return_invoice_number(return_invoice_number)
        if not return_delivery:
            return None
        
        return_delivery.status = status
        for key, value in kwargs.items():
            if hasattr(return_delivery, key) and value is not None:
                setattr(return_delivery, key, value)
        
        self.db.commit()
        self.db.refresh(return_delivery)
        return return_delivery

    def get_returns_by_date(self, return_date: str) -> List[ReturnDelivery]:
        return self.db.query(ReturnDelivery).filter(ReturnDelivery.return_date == return_date).all()

    def delete(self, return_invoice_number: str) -> bool:
        return_delivery = self.get_by_return_invoice_number(return_invoice_number)
        if not return_delivery:
            return False
        
        self.db.delete(return_delivery)
        self.db.commit()
        return True

    def _generate_return_invoice_number(self) -> str:
        return f"RET{uuid.uuid4().hex[:10].upper()}"

    def add_tracking(self, tracking_data: dict) -> ReturnTracking:
        tracking = ReturnTracking(**tracking_data)
        self.db.add(tracking)
        self.db.commit()
        self.db.refresh(tracking)
        return tracking

    def get_tracking_by_return_invoice(self, return_invoice_number: str) -> List[ReturnTracking]:
        return self.db.query(ReturnTracking).filter(
            ReturnTracking.return_invoice_number == return_invoice_number
        ).order_by(ReturnTracking.tracking_date.desc()).all()