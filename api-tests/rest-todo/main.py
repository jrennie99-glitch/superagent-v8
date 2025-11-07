"""
REST API - Todo App with Authentication
Built by SuperAgent - Production-Ready API
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import jwt as pyjwt
import uvicorn
from passlib.context import CryptContext

# Configuration
SECRET_KEY = "superagent-test-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI
app = FastAPI(
    title="REST API - Todo App",
    description="Production-ready REST API built by SuperAgent",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory databases (replace with real DB in production)
users_db = {}
todos_db = {}
todo_counter = 0

# Models
class User(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Todo(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: Optional[str] = "medium"

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    created_at: datetime
    updated_at: datetime
    user_id: str

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except pyjwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
async def root():
    return {
        "message": "REST API - Todo App",
        "version": "1.0.0",
        "built_by": "SuperAgent",
        "endpoints": {
            "auth": ["/auth/register", "/auth/login"],
            "todos": ["/todos", "/todos/{id}"],
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "users": len(users_db),
        "todos": len(todos_db)
    }

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
        "created_at": datetime.utcnow()
    }
    
    return UserResponse(
        username=user.username,
        email=user.email,
        created_at=users_db[user.username]["created_at"]
    )

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    if user.username not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user.password, users_db[user.username]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)

# Todo endpoints
@app.get("/todos", response_model=List[TodoResponse])
async def get_todos(username: str = Depends(verify_token)):
    user_todos = [
        todo for todo in todos_db.values()
        if todo["user_id"] == username
    ]
    return user_todos

@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: Todo, username: str = Depends(verify_token)):
    global todo_counter
    todo_counter += 1
    
    new_todo = {
        "id": todo_counter,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
        "priority": todo.priority,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "user_id": username
    }
    
    todos_db[todo_counter] = new_todo
    return TodoResponse(**new_todo)

@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int, username: str = Depends(verify_token)):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo = todos_db[todo_id]
    if todo["user_id"] != username:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return TodoResponse(**todo)

@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo: Todo, username: str = Depends(verify_token)):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    existing_todo = todos_db[todo_id]
    if existing_todo["user_id"] != username:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    existing_todo.update({
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
        "priority": todo.priority,
        "updated_at": datetime.utcnow()
    })
    
    return TodoResponse(**existing_todo)

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, username: str = Depends(verify_token)):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo = todos_db[todo_id]
    if todo["user_id"] != username:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    del todos_db[todo_id]
    return None

if __name__ == "__main__":
    print("🚀 Starting REST API - Todo App")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🏥 Health Check: http://localhost:8001/health")
    uvicorn.run(app, host="0.0.0.0", port=8001)
