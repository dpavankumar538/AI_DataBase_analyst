from app.database.base import Base
from app.database.connection import engine
from app.models import Customer

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")