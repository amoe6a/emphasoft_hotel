# 🏨 Emphasoft Hotel Booking API

[![Django Version](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django)](#)
[![Django REST Framework](https://img.shields.io/badge/DRF-red?style=for-the-badge&logo=django)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](#)
[![Koyeb Deployment](https://img.shields.io/badge/Deployed_on-Koyeb-blueviolet?style=for-the-badge&logo=koyeb)](#)

A full-stack web application designed for managing hotel room reservations. This project features a classic Django web interface for server-side rendered pages alongside a robust Django REST Framework (DRF) API for client consumption.

> **Live Demo:** [View on Koyeb](https://bloody-nonna-amoebae-938ffef2.koyeb.app/accounts/login/)

---

## 🛠️ Tech Stack

* **Backend:** Django
* **API Framework:** Django REST Framework (DRF)
* **Database:** PostgreSQL (Development & Production)
* **Frontend:** Django Templates, HTML5/CSS3 (Bootstrap)
* **Package Management:** `uv`
* **Deployment:** Koyeb

---

## ⚙️ Local Installation & Setup

We recommend using [`uv`](https://github.com/astral-sh/uv) for lightning-fast package management and virtual environment handling.

### 1. Clone the repository
```bash
git clone https://github.com/amoe6a/emphasoft_hotel.git
cd emphasoft_hotel

### 2. Dependencies
```bash
pip install uv
uv sync
uv run python manage.py migrate
uv run python manage.py collectstatic

### Install psql (18.0 +) and then start the server:
```bash
uv run python manage.py runserver

🛠️ Tech Stack
Backend: Django

API: Django REST Framework (DRF)

Database: PostgreSQL (Dev/Production)

Frontend: Django Templates, HTML/CSS (Bootstrap)

Deployment: Koyeb
