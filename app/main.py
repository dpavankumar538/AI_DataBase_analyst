from fastapi import FastAPI,HTTPException
from pydantic import BaseModel 

app = FastAPI()
#Pyadntic model

class Customer(BaseModel):
    id : int
    name : str
    city : str
    
class Customerupdate(BaseModel):
    name : str
    city : str


customers =[
    {"id":1,"name":"Rahul","city":"Hyderabad"},
    {"id":2,"name":"Priya","city":"Bangalore"},
    {"id":3,"name":"Arjun","city":"Chennai"}
]

@app.get("/")
def home():
    return {"message":"Welcome to AI-Database Analysis"}

@app.get("/customers")
def get_customers():
    return customers

@app.post("/customers",status_code=201)
def add_customers(customer : Customer):
    for existing_customer in customers:
        if existing_customer["id"]==customer.id:
            raise HTTPException(
                status_code=409,
                detail ="Customer Id already exists"
            )
    customers.append(customer.model_dump())
    return(
        {"message":"Customer Added Successfully",
         "customer":customer
        }
    )
    
    
@app.put("/customer/{customer_id}",status_code=201)
def update_customer(customer_id:int,updated_customer:Customerupdate):
    for existing_customer in customers:
        if existing_customer["id"] == customer_id:
            
            existing_customer["name"] = updated_customer.name
            existing_customer["city"] = updated_customer.city
            
            return(
                {
                    "message":"Customer Updated Successsfully",
                    "customer":existing_customer
                }
            )
    raise HTTPException(
        detail="Customer Not found",
        status_code = 404
    )    


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id:int):
    for existing_customers in customers:
        if existing_customers["id"] == customer_id:
            customers.remove(existing_customers)
            return({
                "message":"Customer Deleted Successfully",
                "customer":existing_customers
            }     
            )
    raise HTTPException(
        detail="customer not found",
        status_code=404
    )
    