
from fastapi import FastAPI
from app.routes.customers import router as customer_router
from app.routes.auth import router as auth_router

app = FastAPI(
    title="AI Data Analysis API",
    description="AI-powered data analysis application",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Welcome to AI-Database Analysis"}

app.include_router(customer_router)
app.include_router(auth_router)
