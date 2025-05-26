from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.models.agency import Agency, PostalCode, DeliveryAssignment


class AgencyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_agency(self, agency_data: dict) -> Agency:
        agency = Agency(**agency_data)
        self.db.add(agency)
        try:
            self.db.commit()
            self.db.refresh(agency)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("이미 존재하는 에이전시 ID입니다.")
        return agency

    def get_agency_by_id(self, agency_id: str) -> Optional[Agency]:
        return self.db.query(Agency).filter(Agency.agency_id == agency_id).first()

    def get_agency_by_token(self, token: str) -> Optional[Agency]:
        return self.db.query(Agency).filter(Agency.agency_token == token).first()

    def update_agency_token(self, agency_id: str, token: str) -> Optional[Agency]:
        agency = self.get_agency_by_id(agency_id)
        if not agency:
            return None
        
        agency.agency_token = token
        self.db.commit()
        self.db.refresh(agency)
        return agency

    def deactivate_agency(self, agency_id: str) -> bool:
        agency = self.get_agency_by_id(agency_id)
        if not agency:
            return False
        
        agency.is_active = False
        self.db.commit()
        return True

    def create_postal_code(self, postal_data: dict) -> PostalCode:
        postal_code = PostalCode(**postal_data)
        self.db.add(postal_code)
        try:
            self.db.commit()
            self.db.refresh(postal_code)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("우편번호 등록 중 오류가 발생했습니다.")
        return postal_code

    def create_postal_codes_bulk(self, postal_codes_data: List[dict]) -> List[PostalCode]:
        postal_codes = []
        for postal_data in postal_codes_data:
            postal_code = PostalCode(**postal_data)
            postal_codes.append(postal_code)
            self.db.add(postal_code)
        
        try:
            self.db.commit()
            for postal_code in postal_codes:
                self.db.refresh(postal_code)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("우편번호 목록 등록 중 오류가 발생했습니다.")
        return postal_codes

    def get_postal_codes_by_agency(self, agency_id: str) -> List[PostalCode]:
        return self.db.query(PostalCode).filter(PostalCode.agency_id == agency_id).all()

    def check_postal_code_deliverable(self, agency_id: str, postal_code: str) -> Optional[PostalCode]:
        return self.db.query(PostalCode).filter(
            PostalCode.agency_id == agency_id,
            PostalCode.postal_code == postal_code,
            PostalCode.is_deliverable == True
        ).first()

    def create_delivery_assignment(self, assignment_data: dict) -> DeliveryAssignment:
        assignment = DeliveryAssignment(**assignment_data)
        self.db.add(assignment)
        try:
            self.db.commit()
            self.db.refresh(assignment)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("배송 할당 중 오류가 발생했습니다.")
        return assignment

    def get_assignment_by_invoice(self, invoice_number: str) -> Optional[DeliveryAssignment]:
        return self.db.query(DeliveryAssignment).filter(
            DeliveryAssignment.invoice_number == invoice_number
        ).first()

    def get_assignments_by_agency_and_date(self, agency_id: str, delivery_date: str) -> List[DeliveryAssignment]:
        return self.db.query(DeliveryAssignment).filter(
            DeliveryAssignment.agency_id == agency_id,
            DeliveryAssignment.delivery_date == delivery_date
        ).all()

    def update_assignment_status(self, invoice_number: str, status: str, **kwargs) -> Optional[DeliveryAssignment]:
        assignment = self.get_assignment_by_invoice(invoice_number)
        if not assignment:
            return None
        
        assignment.assignment_status = status
        for key, value in kwargs.items():
            if hasattr(assignment, key) and value is not None:
                setattr(assignment, key, value)
        
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def complete_delivery_assignment(self, invoice_number: str, completion_data: dict) -> Optional[DeliveryAssignment]:
        assignment = self.get_assignment_by_invoice(invoice_number)
        if not assignment:
            return None
        
        for key, value in completion_data.items():
            if hasattr(assignment, key) and value is not None:
                setattr(assignment, key, value)
        
        self.db.commit()
        self.db.refresh(assignment)
        return assignment