from fastapi import FastAPI
from app.auth.routes import authRoutes

app = FastAPI()

app.include_router(authRoutes)

@app.get("/")
async def root():
    return {"message": "Hello World"}