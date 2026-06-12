from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#database setup - create/connect to database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

#database model - what the table will look like
class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    priority = Column(String, index=True)

Base.metadata.create_all(bind=engine) #actually creates the table in the database

#pydantic schema - validates incoming data
class Task(BaseModel):
    title: str
    description: str
    priority: str

#app starts here
app = FastAPI()

#your routes
@app.post("/tasks")
def create_task(task: TaskCreate):
    db = SessionLocal()
    new_task = TaskDB(
        title = task.title,
        description = task.description,
        priority = task.priority
    )
    db.add(new_task)
    db.commit()
    return {"message": "Task created successfully"}

@app.get("/tasks")
def get_tasks():
    db = SessionLocal()
    tasks = db.query(TaskDB).all()
    return tasks
