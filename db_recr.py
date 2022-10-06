from app.database import engine
from app.tables import Base


if __name__ == "__main__":
    print("Creating db....")
    Base.metadata.create_all(engine)