# UniDB — University Management System

A full-stack web application for managing university data — students, instructors, courses, departments, and enrollments — built with a normalized relational database schema.

> DBMS DA-1 Part 2 · 24BAI1355 Vatsal Agrawal

---

## Features

- Full **CRUD** operations on all entities: Students, Instructors, Courses, Departments, Designations, Enrollments, Pincodes, Course-Instructor assignments, and Course Textbooks
- **Normalized schema** up to 3NF with proper foreign key constraints
- **REST API** with JSON responses for all tables
- Clean dark-themed UI with tabbed navigation — no build step required
- Pre-loaded seed data for quick demo

---

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Backend  | Python · Flask                    |
| Database | SQLite (via `sqlite3` stdlib)     |
| Frontend | Vanilla HTML / CSS / JavaScript   |
| API      | RESTful JSON endpoints            |

---

## Setup & Run

```bash
# 1. Install dependency
pip install flask

# 2. Start the server
python app.py

# 3. Open in browser
# http://localhost:5000
```

The SQLite database (`university.db`) is created and seeded automatically on first run.

---

## API Endpoints

All endpoints follow the pattern `/api/<resource>` and support `GET`, `POST`, `PUT /<id>`, `DELETE /<id>`.

| Resource              | Endpoint                    |
|-----------------------|-----------------------------|
| Departments           | `/api/departments`          |
| Designations          | `/api/designations`         |
| Pincodes              | `/api/pincodes`             |
| Students              | `/api/students`             |
| Instructors           | `/api/instructors`          |
| Courses               | `/api/courses`              |
| Course–Instructors    | `/api/course-instructors`   |
| Course Textbooks      | `/api/course-textbooks`     |
| Enrollments           | `/api/enrollments`          |

Each resource also has a `/full` variant (e.g. `/api/students/full`) that returns joined/enriched data.

---

## Database Schema (3NF)

```
DEPARTMENT   (department_id PK, department_name, location)
DESIGNATION  (designation_id PK, designation_name, base_salary)
PINCODE      (pincode PK, city, state)
STUDENT      (student_id PK, first_name, last_name, dob, email, phone,
              street, pincode FK, year_of_study, department_id FK)
INSTRUCTOR   (instructor_id PK, name, email, phone, designation_id FK)
COURSE       (course_id PK, course_name, credits, semester, department_id FK)
COURSE_INSTRUCTOR  (id PK, course_id FK, instructor_id FK)
COURSE_TEXTBOOK    (id PK, course_id FK, textbook)
ENROLLMENT   (enrollment_id PK, student_id FK, course_id FK, grade, enrollment_date)
```

### Normalization Summary

**1NF** — Decomposed composite attributes: `Name` → `first_name + last_name`; `Address` → `street + pincode` (with `PINCODE` lookup table for city/state).

**2NF** — All tables have single-column primary keys, so no partial dependencies exist.

**3NF** — Removed transitive dependency `Instructor_ID → Designation → Salary` by extracting the `DESIGNATION` table.

---

## Project Structure

```
university-db/
├── app.py              # Flask app — DB init, CRUD factory, routes
├── requirements.txt    # Python dependencies (flask)
├── university.db       # SQLite database (auto-generated)
└── templates/
    └── index.html      # Single-page frontend
```
