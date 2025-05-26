# TodayPickup API Implementation

이 프로젝트는 TodayPickup API (https://admin.todaypickup.com/v2/api-docs)의 모든 엔드포인트를 호출할 수 있는 FastAPI 서비스입니다.

## 구조

### 계층별 구조
- **Models**: 데이터베이스 엔터티 정의
- **Schemas**: 요청/응답 검증을 위한 Pydantic 스키마
- **Repositories**: 데이터베이스 작업 처리
- **Services**: 비즈니스 로직 및 외부 API 호출
- **Controllers**: HTTP 엔드포인트 정의

### API 그룹

#### 1. Mall Open API (`/api/mall`)
- 배송 등록 (단건/복수건)
- 배송 조회 (단건/복수건)
- 배송 가능 여부 확인
- 배송 취소
- 반품 요청
- 반품 등록 (단건/복수건)

#### 2. Agency Open API (`/api/agency`)
- 인증 토큰 검증 및 생성
- 배송 완료 처리
- 플렉스 이관
- 배송 상태 업데이트
- 배송 목록 조회
- 우편번호 관리

#### 3. 내부 관리 API
- 에이전시 관리
- 배송 할당
- 데이터 조회 및 관리

## 주요 파일

### Models
- `app/models/delivery.py`: 배송 관련 테이블
- `app/models/return_delivery.py`: 반품 관련 테이블
- `app/models/agency.py`: 에이전시 관련 테이블

### Services
- `app/services/today_pickup_client.py`: 외부 API 호출 클라이언트
- `app/services/delivery_service.py`: 배송 비즈니스 로직
- `app/services/return_service.py`: 반품 비즈니스 로직
- `app/services/agency_service.py`: 에이전시 비즈니스 로직

### Controllers
- `app/controllers/today_pickup_delivery_controller.py`: 배송 API 엔드포인트
- `app/controllers/today_pickup_return_controller.py`: 반품 API 엔드포인트
- `app/controllers/today_pickup_agency_controller.py`: 에이전시 API 엔드포인트

## 테스트

### 단위 테스트
```bash
# 모든 테스트 실행
pytest

# 특정 서비스 테스트
pytest tests/test_delivery_service.py
pytest tests/test_return_service.py
pytest tests/test_agency_service.py

# 커버리지 포함 테스트
pytest --cov=app --cov-report=html
```

### 테스트 파일
- `tests/test_delivery_service.py`: 배송 서비스 테스트
- `tests/test_return_service.py`: 반품 서비스 테스트
- `tests/test_agency_service.py`: 에이전시 서비스 테스트

## 데이터베이스

### 마이그레이션
```bash
# 새로운 마이그레이션 생성
alembic revision --autogenerate -m "migration_name"

# 마이그레이션 적용
alembic upgrade head
```

### 테이블
- `deliveries`: 배송 정보
- `delivery_trackings`: 배송 추적 정보
- `return_deliveries`: 반품 정보
- `return_trackings`: 반품 추적 정보
- `agencies`: 에이전시 정보
- `postal_codes`: 우편번호 정보
- `delivery_assignments`: 배송 할당 정보

## 사용법

### 서버 실행
```bash
uvicorn app.main:app --reload
```

### API 문서
서버 실행 후 다음 URL에서 API 문서 확인:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 인증
모든 외부 API 호출에는 Bearer 토큰이 필요합니다:
```
Authorization: Bearer your_token_here
```

## 주요 기능

### 1. 배송 등록
```python
POST /api/mall/deliveryRegister
{
    "sender_name": "발송자",
    "sender_phone": "010-1234-5678",
    "receiver_name": "수령자",
    "receiver_phone": "010-9876-5432",
    "product_name": "상품명",
    "product_quantity": 1,
    "payment_type": "PREPAID"
}
```

### 2. 배송 조회
```python
GET /api/mall/delivery/{invoice_number}
```

### 3. 에이전시 토큰 검증
```python
POST /api/agency/auth
{
    "agency_id": "AGENCY_001",
    "token": "your_token"
}
```

## 환경 설정

### 필수 패키지
- FastAPI
- SQLAlchemy
- Pydantic
- httpx (외부 API 호출)
- pytest (테스트)

### 데이터베이스
- PostgreSQL (운영)
- SQLite (테스트)

## 개발 노트

- 모든 외부 API 호출은 `TodayPickupClient`를 통해 수행
- 에러 처리 및 로깅 포함
- 단위 테스트로 80% 이상 커버리지 유지
- Repository 패턴으로 데이터 접근 레이어 분리
- Service 레이어에서 비즈니스 로직 처리