# Placement Portal V2 - Institute Recruitment Platform
Description  

A role-based Single-Page Web Application (SPA) that automates campus recruitment activities for Students, Companies, and the Placement Admin. 

Technologies used
1. Backend & Flask Extensions (Python) 
Flask (v2.3.3) 
Flask-SQLAlchemy (v3.1.1) 
Flask-JWT-Extended (v4.5.3) 
Flask-CORS (v4.0.0) 
Flask-Caching (v2.1.0 
Werkzeug Security 
2. Frontend & UI Libraries (Javascript / Vue) 
Vue 3 (v3.3.4) 
Vite (v4.4.9) 
Vue Router (v4.2.4) 
Axios (v1.5.0) 
Bootstrap 5 & Bootstrap Icons: 
Responsive CSS layout engine providing pre-styled utility classes, grids, buttons, badges, popup 
modals, and iconography. 
Chart.js & vue-chartjs (v4.3.3): Data visualization library used to render interactive Doughnut and 
Bar analytics charts on the Admin Dashboard. 
3. Database & Storage 
SQLite3 :  
Lightweight, zero-configuration relational database embedded directly into the application 
directory (placement_portal.sqlite3). 
4. Asynchronous Processing & Background Tasks 
Celery (v5.3.4) 
Distributed task queue used for user-triggered async jobs (e.g. CSV history export) and 
scheduled periodic tasks (e.g. daily deadline reminders & monthly reports). 
Redis (v5.0.0) 
In-memory data storage engine used as the Celery Message Broker and Result Backend. 

DB Schema Design
<img width="1296" height="818" alt="image" src="https://github.com/user-attachments/assets/c23109ea-7886-4116-a56d-33a2fefb7e6d" />

API Design  
The application implements a RESTful JSON API built with Flask Blueprints (/api/*) to handle data exchange between the Vue 3 frontend and the SQLite database. 

Architecture and Features  
The project follows a decoupled Single-Page Application (SPA) architecture. The controllers (API Endpoints) reside in backend/routes/*.py as Flask Blueprints, while database models live in backend/models.py. The views and templates reside in frontend/src/views/*.vue as Vue 3 components, styled with Bootstrap 6. 
Flask (app.py) handles API routing and serves the compiled Vue frontend (frontend/dist/). 

Additional Features: 
Offer Letter Generator: Company generates printable offer letter previews for 
selected candidates. 

Interactive Analytics: Chart.js Doughnut and Bar charts for drive and application 
statistics. 

Static ATS Resume Preview: Simulated keyword matching score preview for 
students.
