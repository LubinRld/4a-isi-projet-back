import app.database
from fastapi import FastAPI
from app.auth.routes import authRoutes
from app.users.routes import userRoutes
from app.products.routes import productRoutes
from app.closure_days.routes import closureDaysRoutes

app = FastAPI()

app.include_router(authRoutes)
app.include_router(userRoutes)
app.include_router(productRoutes)
app.include_router(closureDaysRoutes)

@app.get("/")
async def root():
    return {"message": "Hello World"}