from fastapi import FastAPI
from api.routers import task
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.include_router(task.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 Origin 허용
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # OPTIONS 메서드 허용
    allow_headers=["*"],
)