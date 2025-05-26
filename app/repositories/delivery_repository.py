from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid

from app.models.delivery import Delivery, DeliveryTracking


class DeliveryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, delivery_data: dict) -> Delivery:
        delivery_data["invoice_number"] = self._generate_invoice_number()
        delivery = Delivery(**delivery_data)
        self.db.add(delivery)
        try:
            self.db.commit()
            self.db.refresh(delivery)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("배송 등록 중 오류가 발생했습니다.")
        return delivery

    def create_multiple(self, deliveries_data: List[dict]) -> List[Delivery]:
        deliveries = []
        for delivery_data in deliveries_data:
            delivery_data["invoice_number"] = self._generate_invoice_number()
            delivery = Delivery(**delivery_data)
            deliveries.append(delivery)
            self.db.add(delivery)
        
        try:
            self.db.commit()
            for delivery in deliveries:
                self.db.refresh(delivery)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("배송 목록 등록 중 오류가 발생했습니다.")
        return deliveries

    def get_by_invoice_number(self, invoice_number: str) -> Optional[Delivery]:
        return self.db.query(Delivery).filter(Delivery.invoice_number == invoice_number).first()

    def get_by_invoice_numbers(self, invoice_numbers: List[str]) -> List[Delivery]:
        return self.db.query(Delivery).filter(Delivery.invoice_number.in_(invoice_numbers)).all()

    def update_status(self, invoice_number: str, status: str, **kwargs) -> Optional[Delivery]:
        delivery = self.get_by_invoice_number(invoice_number)
        if not delivery:
            return None
        
        delivery.status = status
        for key, value in kwargs.items():
            if hasattr(delivery, key) and value is not None:
                setattr(delivery, key, value)
        
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def transfer_to_flex(self, invoice_number: str) -> Optional[Delivery]:
        delivery = self.get_by_invoice_number(invoice_number)
        if not delivery:
            return None
        
        delivery.is_flex = True
        delivery.status = "FLEX_TRANSFERRED"
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def get_deliveries_by_date(self, delivery_date: str) -> List[Delivery]:
        return self.db.query(Delivery).filter(Delivery.delivery_date == delivery_date).all()

    def delete(self, invoice_number: str) -> bool:
        delivery = self.get_by_invoice_number(invoice_number)
        if not delivery:
            return False
        
        self.db.delete(delivery)
        self.db.commit()
        return True

    def _generate_invoice_number(self) -> str:
        return f"INV{uuid.uuid4().hex[:10].upper()}"

    def add_tracking(self, tracking_data: dict) -> DeliveryTracking:
        tracking = DeliveryTracking(**tracking_data)
        self.db.add(tracking)
        self.db.commit()
        self.db.refresh(tracking)
        return tracking

    def get_tracking_by_invoice(self, invoice_number: str) -> List[DeliveryTracking]:
        return self.db.query(DeliveryTracking).filter(
            DeliveryTracking.invoice_number == invoice_number
        ).order_by(DeliveryTracking.tracking_date.desc()).all()