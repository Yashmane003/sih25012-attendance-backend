# Rural Attendance Backend (SIH25012)

Backend APIs for Automated Attendance System (Rural Schools)

## Tech
- Django + DRF
- JWT Authentication
- MySQL

## Setup
1) Create venv
2) Install requirements
3) Create `.env` using `.env.example`
4) Run migrations
5) Run server

## Setup Instructions 

### 1. Clone repository
```bash
git clone <repo_url>
cd rural_attendance_backend

### 2. Create venv
python -m venv venv
venv\Scripts\activate

### 3. Install requirements
pip install -r requirements.txt

### 4.Create .env file using .env.example

### 5. Run Migration
python manage.py makemigrations
python manage.py migrate

### 6. Create Admin
python manage.py createsuperuser

### 7. Run server
python manage.py runserver


