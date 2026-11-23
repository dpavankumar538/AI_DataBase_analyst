from app.database.base import Base
from app.database.connection import engine
import app.models  # noqa: F401 — registers all models

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
