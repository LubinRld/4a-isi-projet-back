from fastapi import FastAPI
from app.auth.routes import authRoutes
from app.users.routes import userRoutes

app = FastAPI()

app.include_router(authRoutes)
app.include_router(userRoutes)

@app.get("/")
async def root():
    return {"message": "Hello World"}