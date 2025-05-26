from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.user_controller import UserController
from app.controllers.today_pickup_delivery_controller import TodayPickupDeliveryController
from app.controllers.today_pickup_return_controller import TodayPickupReturnController
from app.controllers.today_pickup_agency_controller import TodayPickupAgencyController
from app.config.database import engine, Base

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI 서비스",
    description="FastAPI를 사용한 RESTful API 서비스",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
user_controller = UserController()
delivery_controller = TodayPickupDeliveryController()
return_controller = TodayPickupReturnController()
agency_controller = TodayPickupAgencyController()

app.include_router(user_controller.router)
app.include_router(delivery_controller.router)
app.include_router(return_controller.router)
app.include_router(agency_controller.router)

@app.get("/")
async def root():
    return {"message": "환영합니다! FastAPI 서비스입니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 