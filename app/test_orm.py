from app.database.session import SessionLocal
from app.models.customer import Customer

db = SessionLocal()

# new_customer = Customer(
#     name="vinay ORM",
#     city="Hyderabad"
# )

# db.add(new_customer)
# db.commit()

# print("Customer inserted successfully!")

# db.close()
#All records
customers = db.query(Customer).all()

# only conditional records like where
# customer =db.query(Customer).filter(Customer.name=="pavan")

# filter() only retrives first record
# customer = db.query(Customer).filter(Customer.name=="pavan").first()

# for printing customers
# for customer in customers:
#     print(customer.id, customer.name, customer.city)
# db.close()

## Updating Cutomer details
# customer = db.query(Customer).filter(
#     Customer.name=="Pavan Orm").first()

# if customer:
#     customer.city = "Bangalore"
    
#     db.commit()
#     print("customer Updated Successfully")
    
# else:
#     print("customer not found")    
    
# db.close()

## deleting from table 
customer = db.query(Customer).filter(
    Customer.name == "pavan ORM"
).first()

if customer:
    db.delete(customer)
    db.commit()

    print("Customer deleted successfully!")
else:
    print("Customer not found")

db.close()