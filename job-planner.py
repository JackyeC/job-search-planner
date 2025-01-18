from datetime import datetime
import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Data Models
class JobApplication(BaseModel):
    id: Optional[int] = None
    company: str
    position: str
    status: str  # Applied, Interview, Offer, Rejected
    date_applied: datetime
    url: Optional[str] = None
    notes: Optional[str] = None
    
class Task(BaseModel):
    id: Optional[int] = None
    title: str
    due_date: datetime
    completed: bool = False
    job_application_id: Optional[int] = None
    
class Contact(BaseModel):
    id: Optional[int] = None
    name: str
    company: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

class Document(BaseModel):
    id: Optional[int] = None
    title: str
    type: str  # Resume, Cover Letter
    version: str
    last_updated: datetime
    file_path: str

# Database Setup
def init_db():
    conn = sqlite3.connect('job_planner.db')
    cur = conn.cursor()
    
    # Create tables
    cur.executescript('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            status TEXT NOT NULL,
            date_applied TIMESTAMP NOT NULL,
            url TEXT,
            notes TEXT
        );
        
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            due_date TIMESTAMP NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            job_application_id INTEGER,
            FOREIGN KEY (job_application_id) REFERENCES job_applications (id)
        );
        
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            company TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            notes TEXT
        );
        
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            version TEXT NOT NULL,
            last_updated TIMESTAMP NOT NULL,
            file_path TEXT NOT NULL
        );
    ''')
    
    conn.commit()
    conn.close()

# FastAPI App
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Job Planner API! Use the following endpoints:",
        "endpoints": {
            "/applications/": "Manage job applications",
            "/tasks/": "Create and manage tasks",
            "/contacts/": "Manage professional contacts",
            "/documents/": "Store and retrieve documents",
            "/analytics/application-status": "View application stats"
        }
    }


# Job Applications endpoints
@app.post("/applications/", response_model=JobApplication)
async def create_application(application: JobApplication):
    conn = sqlite3.connect('job_planner.db')
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO job_applications (company, position, status, date_applied, url, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (application.company, application.position, application.status,
          application.date_applied, application.url, application.notes))
    
    application.id = cur.lastrowid
    conn.commit()
    conn.close()
    return application

@app.get("/applications/", response_model=List[JobApplication])
async def get_applications():
    conn = sqlite3.connect('job_planner.db')
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM job_applications')
    applications = []
    for row in cur.fetchall():
        applications.append(JobApplication(
            id=row[0],
            company=row[1],
            position=row[2],
            status=row[3],
            date_applied=row[4],
            url=row[5],
            notes=row[6]
        ))
    
    conn.close()
    return applications

# Tasks endpoints
@app.post("/tasks/", response_model=Task)
async def create_task(task: Task):
    conn = sqlite3.connect('job_planner.db')
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO tasks (title, due_date, completed, job_application_id)
        VALUES (?, ?, ?, ?)
    ''', (task.title, task.due_date, task.completed, task.job_application_id))
    
    task.id = cur.lastrowid
    conn.commit()
    conn.close()
    return task

@app.put("/tasks/{task_id}/complete")
async def complete_task(task_id: int):
    conn = sqlite3.connect('job_planner.db')
    cur = conn.cursor()
    
    cur.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    conn.commit()
    conn.close()
    return {"message": "Task marked as completed"}

# Contacts endpoints
@app.post("/contacts/", response_model=Contact)
async def create_contact(contact: Contact):
    conn = sqlite3.connect('job_planner.db')
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO contacts (name, company, email, phone, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (contact.name, contact.company, contact.email, contact.phone, contact.notes))
    
    contact.id = cur.lastrowid
    conn.commit()
    conn.close()
    return contact

# Documents endpoints
@app.post("/documents/", response_model=Document)
async def create_document(document: Document):
    conn = sqlite3.connect('job_planner.db')
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO documents (title, type, version, last_updated, file_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (document.title, document.type, document.version,
          document.last_updated, document.file_path))
    
    document.id = cur.lastrowid
    conn.commit()
    conn.close()
    return document

# Analytics endpoints
@app.get("/analytics/application-status")
async def get_application_stats():
    conn = sqlite3.connect('job_planner.db')
    cur = conn.cursor()
    
    cur.execute('''
        SELECT status, COUNT(*) as count
        FROM job_applications
        GROUP BY status
    ''')
    
    stats = {}
    for row in cur.fetchall():
        stats[row[0]] = row[1]
    
    conn.close()
    return stats

if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
