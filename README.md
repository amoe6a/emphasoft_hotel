Hotel Booking System, for Emphasoft 
A full-stack Django application for managing hotel room reservations. This project features a classic Django web interface and a Django REST Framework (DRF) API. Swagger available at /api/docs/

Deployed on Koyeb:
https://bloody-nonna-amoebae-938ffef2.koyeb.app/accounts/login/


Installation
Clone the repository:

Bash
git clone https://github.com/amoe6a/emphasoft_hotel.git
cd emphasoft_hotel

Dependencies
Bash
pip install uv
uv sync
uv run python manage.py migrate
uv run python manage.py collectstatic

Start the server:
uv run python manage.py runserver

🛠️ Tech Stack
Backend: Django

API: Django REST Framework (DRF)

Database: PostgreSQL (Dev/Production)

Frontend: Django Templates, HTML/CSS (Bootstrap)

Deployment: Koyeb