import app.database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import authRoutes
from app.users.routes import userRoutes
from app.products.routes import productRoutes
from app.closure_days.routes import closureDaysRoutes
from app.menus.routes import menuRoutes
from app.orders.routes import orderRoutes

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

app.include_router(authRoutes)
app.include_router(userRoutes)
app.include_router(productRoutes)
app.include_router(closureDaysRoutes)
app.include_router(menuRoutes)
app.include_router(orderRoutes)

@app.get("/")
async def root():
    return {"message": "Hello World"}