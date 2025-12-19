# Blog
# Blogging Platform API

## Description

This project is a RESTful Blogging Platform built with **Django** and **Django Rest Framework (DRF)**. It allows users to create, read, update and delete blog posts with **fine‑grained read and write permissions**, as well as interact with posts through **likes** and **comments**. The platform also includes **team‑based permissions**, **user roles**, and a fully configured **Django admin panel**.

---

## Features

* User authentication (login/logout)
* User roles: **admin** and **blogger**
* Team-based access control (each user belongs to exactly one team)
* Blog post permissions with independent **read** and **write** controls
* CRUD operations for blog posts
* Like and unlike functionality
* Comment creation and deletion
* Pagination for posts, likes and comments
* Django admin panel with full permissions

---

## Tech Stack

* Python
* Django
* Django Rest Framework
* SQLite / PostgreSQL (depending on environment)

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <project-folder>
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\\Scripts\\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create superuser (site admin)

```bash
python manage.py createsuperuser
```

### 6. Run development server

```bash
python manage.py runserver
```

---

## Authentication

* Authentication is handled using Django / DRF authentication mechanisms.
* Users must be authenticated to:

  * Create posts
  * Like or unlike posts
  * Comment on posts
* Non‑authenticated users can only view posts that have **public read access**.

---

## User Roles

* **Admin (role)**: Can read, edit and delete any post regardless of permissions.
* **Blogger**: Access is restricted by post permissions.

> Note: The **admin role** is different from the **Django site admin** (`is_staff`).

---

## Post Permissions

Each blog post has **independent read and write permissions** for the following levels:

* **Public**: Anyone can access
* **Authenticated**: Any logged‑in user
* **Team**: Users in the same team as the author
* **Author**: Only the post author

### Example:

* Public: Read only
* Authenticated: Read only
* Team: Read and write
* Author: Read and write

Permissions are validated before any read, edit or delete operation.

---

## API Endpoints

### Posts

| Method | Endpoint         | Description           |
| ------ | ---------------- | --------------------- |
| POST   | /api/posts/      | Create a blog post    |
| GET    | /api/posts/      | List accessible posts |
| GET    | /api/posts/{id}/ | Retrieve post details |
| PUT    | /api/posts/{id}/ | Update post           |
| DELETE | /api/posts/{id}/ | Delete post           |

### Likes

| Method | Endpoint              | Description             |
| ------ | --------------------- | ----------------------- |
| POST   | /api/posts/{id}/like/ | Like a post             |
| DELETE | /api/posts/{id}/like/ | Unlike a post           |
| GET    | /api/likes/           | List likes (filterable) |

### Comments

| Method | Endpoint            | Description                |
| ------ | ------------------- | -------------------------- |
| POST   | /api/comments/      | Create comment             |
| GET    | /api/comments/      | List comments (filterable) |
| DELETE | /api/comments/{id}/ | Delete own comment         |

---

## Pagination

* Posts: 10 per page
* Comments: 10 per page
* Likes: 20 per page

Pagination responses include:

* Current page
* Total pages
* Total count
* Next page URL
* Previous page URL

---

## Admin Panel

* Django admin panel is enabled
* Site admins can perform full CRUD operations on:

  * Users
  * Posts
  * Comments
  * Likes

---

## Evaluation Criteria Coverage

This project satisfies the evaluation requirements by implementing:

* Proper database design
* Authentication and role‑based permissions
* RESTful API with CRUD operations
* Like and comment functionality
* Admin panel configuration
* Clean and organized codebase

---

## Authors

Developed as part of a Django REST Framework lab project.
