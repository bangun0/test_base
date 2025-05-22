# FastAPI 서비스

FastAPI를 사용한 RESTful API 서비스 예제입니다.

## 프로젝트 구조

```
app/
├── config/           # 설정 관련 코드
├── controllers/      # 컨트롤러 레이어 (API 엔드포인트 정의)
├── models/           # 데이터베이스 모델 (ORM)
├── repositories/     # 저장소 레이어 (데이터베이스 접근)
├── schemas/          # Pydantic 스키마 (요청/응답 데이터 검증)
├── services/         # 서비스 레이어 (비즈니스 로직)
└── main.py           # 애플리케이션 진입점
```

## 설치 및 실행

1. 가상 환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 데이터베이스 설정
```bash
# PostgreSQL을 설치하고 다음 정보로 데이터베이스 생성
# 데이터베이스: db_test
# 사용자: user_test
# 비밀번호: user_test
```

4. 데이터베이스 마이그레이션 실행
```bash
alembic upgrade head
```

5. 서버 실행
```bash
uvicorn app.main:app --reload
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

외부 TodayPickup API에 대한 프록시 엔드포인트는 `/todaypickup` 경로 아래에 위치합니다. 예를 들어 `GET /todaypickup/v2/some-endpoint`와 같이 호출할 수 있습니다.
