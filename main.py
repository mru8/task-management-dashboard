from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import sessionmaker
from fastapi import Depends

class Base(DeclarativeBase):
    pass
#database setup - create/connect to database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

#database model - what the table will look like
class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    priority = Column(String, index=True)

Base.metadata.create_all(bind=engine) #actually creates the table in the database

#pydantic schema - validates incoming data
class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str

#app starts here
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#your routes
@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db = SessionLocal()
    try:
        new_task = TaskDB(
            title = task.title,
            description = task.description,
            priority = task.priority
        )
        db.add(new_task)
        db.commit()
        return {"message": "Task created successfully"}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    db = SessionLocal()
    # tasks = db.query(TaskDB).all()
    # return tasks
    try:
        tasks = db.query(TaskDB).all()
        return tasks
    finally:
        db.close()
