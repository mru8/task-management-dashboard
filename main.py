from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, HTTPException

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

Base.metadata.create_all(bind=engine) 

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str

class TaskResponse(BaseModel):
    id: int
    title: str
    description:str
    priority: str
    model_config = {"from_attributes": True}

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    try:
        new_task = TaskDB(
            title = task.title,
            description = task.description,
            priority = task.priority
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except Exception:
        db.rollback()
        raise

@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(TaskDB).all()

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    existing_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    existing_task.title = task.title
    existing_task.description = task.description
    existing_task.priority = task.priority
    db.commit()
    db.refresh(existing_task)
    return existing_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id:int, db: Session = Depends(get_db)):
    existing_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(existing_task)
    db.commit()
    return {"message":"Task deleted successfully"}