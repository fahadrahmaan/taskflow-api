# TaskFlow

TaskFlow is a backend-focused task management project built with Django and Django REST Framework.

The main purpose of this project is to demonstrate practical backend concepts such as REST API development, JWT authentication, Redis caching, rate limiting, secure user-level data access, PostgreSQL integration, and Docker-based setup.

Alongside the API layer, I also added a lightweight Django template-based dashboard so the project can be used and demonstrated through a clean web interface as well.

---

## What this project covers

This project was built to showcase backend engineering concepts in a practical CRUD application.

It includes:

- RESTful task management APIs using Django REST Framework
- JWT-based authentication using SimpleJWT
- User-specific task access control
- Task filtering by status and priority
- Pagination for API responses
- Redis-based caching for task list responses
- Redis-based rate limiting (20 requests/minute per user)
- PostgreSQL database integration
- Docker and Docker Compose support
- Django template-based dashboard for end-to-end usability

---

## Tech Stack

- Django
- Django REST Framework
- PostgreSQL
- Redis
- SimpleJWT
- Docker
- Docker Compose
- Gunicorn
- dj-database-url

---

## Main Features

### API Features

- User registration
- JWT authentication
- Create, read, update, and delete tasks
- User-specific task isolation
- Filtering by status and priority
- Pagination for task list responses
- Redis caching for task retrieval
- Redis-based rate limiting

### Dashboard Features

- User registration and login
- Create, edit, delete, and view tasks
- Clickable task detail page
- Add and update notes for individual tasks
- Toggle task status directly from the dashboard
- Newest tasks shown first
- Success messages for registration, create, edit, delete, and note updates

### Validation and Security

- Deadline validation to prevent past dates
- Required title validation
- Title length restriction
- Unique username validation
- Confirm password validation during registration
- Protected dashboard routes using `login_required`
- Safe object access using `get_object_or_404`
- Cache prevention for protected pages after logout

### Admin Insights

A custom admin insights page is available for superusers, showing:

- Total users
- Total tasks
- Completed tasks
- Pending tasks
- High-priority tasks
- Overdue pending tasks

It also includes the ability to delete users from the custom admin page.

---

## API Endpoints

### Authentication

- `POST /api/register/` → create a new user
- `POST /api/login/` → get JWT access and refresh tokens
- `POST /api/token/refresh/` → refresh access token

### Tasks

Base endpoint:

`/api/tasks/`

Supported operations:

- `GET /api/tasks/`
- `POST /api/tasks/`
- `PUT /api/tasks/{id}/`
- `DELETE /api/tasks/{id}/`

All task operations are restricted to the authenticated user's data.

---

## Filtering

Examples:

- `/api/tasks/?status=pending`
- `/api/tasks/?priority=high`

---

## Redis Usage

Redis is used in two ways in this project:

1. Caching task list responses to reduce repeated database queries
2. Applying a per-user rate limit on the task list endpoint

Current rate limit:

- 20 requests per minute per user

If the limit is exceeded, the API returns `HTTP 429 Too Many Requests`.

---

## Local Setup

### Run locally with virtual environment

```bash id="6cfb1v"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

Run with Docker
docker compose up --build
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

Then open:

http://127.0.0.1:8000/

Project Structure

taskflow/
│
├── taskflow/
│   ├── settings.py
│   ├── urls.py
│
├── tasks/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│
├── templates/
│   └── tasks/
│       ├── base.html
│       ├── home.html
│       ├── register.html
│       ├── login.html
│       ├── dashboard.html
│       ├── create_task.html
│       ├── edit_task.html
│       ├── task_detail.html
│       ├── admin_insights.html
│
├── requirements.txt
├── README.md
├── Documentation.txt
├── Dockerfile
├── docker-compose.yml
├── manage.py

Live API

https://taskflow-api-yg28.onrender.com/api/tasks/

Repository

https://github.com/fahadrahmaan/taskflow

Author

Fahad Rahman