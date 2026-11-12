from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

@router.get("/")
def get_customers(db: Session = Depends(get_db)):

    customers = db.query(Customer).all()

    return [
        {
            "id": customer.id,
            "name": customer.name,
            "city": customer.city
        }
        for customer in customers
    ]

@router.post("/", status_code=201)
def add_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    new_customer = Customer(
        name=customer.name,
        city=customer.city
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return {
        "message": "Customer added successfully",
        "customer": {
            "id": new_customer.id,
            "name": new_customer.name,
            "city": new_customer.city
        }
    }

@router.put("/{customer_id}")
def update_customer(
    customer_id : int,
    updated_customer: CustomerUpdate,
    db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()
    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
    
    customer.name = updated_customer.name
    customer.city = updated_customer.city

    db.commit()
    db.refresh(customer)

    return {
        "message": "Customer updated successfully",
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "city": customer.city
        }
    }

@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    db.delete(customer)
    db.commit()

    return {
        "message": "Customer deleted successfully",
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "city": customer.city
        }
    }