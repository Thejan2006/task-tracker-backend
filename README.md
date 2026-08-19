# 🚀 Task & Resource Tracker - Backend API

This repository contains the backend RESTful API for the **Cloud-Native Task & Resource Tracker** application. Built using **Python FastAPI**, **PostgreSQL**, and **SQLAlchemy**, and designed to be fully containerized via **Docker**.

---

## 🛠️ Tech Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Data Validation:** Pydantic
* **Containerization:** Docker
* **Architecture:** Microservices / Polyrepo

---

## 🎯 Key Features

- **CRUD Operations:** Create, Read, Update, and Delete task items.
- **RESTful Endpoints:** Auto-documented endpoints via OpenAPI / Swagger UI.
- **ORM Integration:** Database modeling and connection management using SQLAlchemy.
- **Dockerized Ready:** Configured for isolated container deployment.

---

## 📂 Project Structure

```text
task-tracker-backend/
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── database.py      # Database connection setup
│   └── models.py        # SQLAlchemy database models
├── requirements.txt     # Python dependencies
└── README.md
