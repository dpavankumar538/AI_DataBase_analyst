
from fastapi import FastAPI
from app.routes.customers import router as customer_router

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Welcome to AI-Database Analysis"}

app.include_router(customer_router)

