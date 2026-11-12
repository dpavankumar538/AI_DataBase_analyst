from app.database.session import SessionLocal
from app.models.customer import Customer
from app.models.order import Order
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
# customers = db.query(Customer).all()

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
# customer = db.query(Customer).filter(
#     Customer.name == "pavan ORM"
# ).first()

# if customer:
#     db.delete(customer)
#     db.commit()

#     print("Customer deleted successfully!")
# else:
#     print("Customer not found")

# db.close()



# new_order = Order(
#     product="Laptop",
#     customer_id=1
# )

# db.add(new_order)
# db.commit()
# db.refresh(new_order)
# print("Order ID:", new_order.id)
# print("Product:", new_order.product)
# print("Customer ID:", new_order.customer_id)
# db.close()

# orders = db.query(Order).all()

# if orders is not None:
#     for order in orders:
#         print("Product:", order.product)
#         print("Customer:", order.customer.name)
#         print("City:", order.customer.city)
#         print("customerId:", order.customer_id)
# else:
#     print("No orders found")

# db.close()


customer = db.query(Customer).filter(
    Customer.id == 1
).first()

if customer is not None:
    print("Customer:", customer.name)

    for order in customer.orders:
        print("Product:", order.product)
else:
    print("Customer not found")

db.close()

# customer = db.query(Customer).filter(
#     Customer.id == 1
# ).first()

# if customer is not None:
#     new_order = Order(product="Mobile")
#     customer.orders.append(new_order)

#     db.commit()
#     print("Order added successfully!")

# db.close()