from sqlalchemy.orm import Session
from app.database import engine
from app.models import DataEntry

def advanced_transaction_example():
    with Session(engine) as session:
        try:
            entry = DataEntry(content="Hello", format="JSON", user_id=1)
            session.add(entry)
            session.commit()  # commits transaction
        except:
            session.rollback()
            raise
        finally:
            session.close()
