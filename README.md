# Blog Platform API

## Project Name
blog_project

## Project Description
blog_project is a RESTful API built with **Django** and **Django Rest Framework** that implements a blogging platform with authentication, team-based permissions, likes, comments, and administrative control.

The project focuses on correct permission handling, clean architecture, and 100% test coverage for mission-critical logic.

## Architecture (C4 Model)

### Level 1: System Context
This diagram shows how different users interact with the Blog API and external services.
```mermaid
graph TD
    %% Entities
    Anonymous((Anonymous User))
    AuthUser((Authenticated User))
    Admin((Administrator))

    System[("Blog Platform System")]

    %% Relationships
    Anonymous -- "View public posts with their comments and likes (details)." --> System

    AuthUser -- "Creates posts and defines editing and visibility permissions." --> System
    AuthUser -- "Views posts based on read visibility levels (public, authenticated users, team)" --> System
    AuthUser -- "Interacts (Likes/Comments) with accessible posts" --> System
    
    Admin -- "Bypasses all privacy restrictions and manages teams" --> System
```
### Level 2: Containers View
This diagram ilustrates the internal parts of the system and how the Backend (Django) serves the Frontend (Angular) and persists data.
```mermaid
graph LR
   User((User / Author)) -- "Interacts via browser" --> Angular
    
    subgraph "Blog Platform System"
        Angular[("Web Application (Angular)")]
        
        API[("API Application (Django / DRF)")]
        
        DB[("Database (PostgreSQL)")]
        
        %% Communication
        Angular -- "API Requests (Cookie Auth)" --> API
        API -- "Read/Write SQL" --> DB
    end
```

### Level 3: Component View (API Logic)
This level shows how the Django API handles a request. It highlights the Permission Layer, which is the core of the business logic.
```mermaid
graph TD
    Req[Angular HTTP Request] --> Auth[Auth Middleware]
    Auth -- "Validate Session Cookie" --> ViewSet[Post ViewSet]
    
    subgraph "Django Internal Logic"
        ViewSet --> Filter[QuerySet Filter]
        Filter -- "Filter by Team/Privacy" --> Serializer[Post Serializer]
        Serializer --> Perm[Custom Permission Classes]
    end

    Perm -- "Check Read/Write" --> DB[(PostgreSQL)]
```
###Database Design (ERD)
This diagram represents the relational structure and how content is linked to users and teams.
```mermaid
erDiagram
    USER ||--o{ POST : "author of"
    USER }|--|| TEAM : "member of"
    POST ||--o{ COMMENT : "contains"
    POST ||--o{ LIKE : "receives"
    USER ||--o{ COMMENT : "writes"
    USER ||--o{ LIKE : "gives"

    USER {
        integer id PK
        string email
        string role "admin/blogger"
    }
    POST {
        integer id PK
        string title
        text content
        string privacy_read
        string privacy_write
    }
    TEAM {
        integer id PK
        string name
    }
```

## Authentication & Core Concepts

### Authentication
- Authentication is handled using **secure cookies**.
- Users can register, log in, and log out.
- Protected endpoints require authentication unless explicitly public.

### Users and Teams
- Each user belongs to exactly one team.
- Only administrators can change team assignments.
- Permissions are evaluated dynamically.
- Access Control: When a user changes teams, they lose access to posts from the previous team, and only the current team determines access. The user’s posts are transferred to the new team and do not remain with the former team.

### Roles
- Admin: Can read and edit any post and bypass all permission restrictions.
- Regular Users: Subject to post-level permissions.

## Permissions System
Read and write permissions are independent.

Available levels:
- Public: anyone can access
- Authenticated: any logged-in user
- Team: users in the author's team
- Author: only the author

Rules:
- Admins bypass restrictions.
- Team permissions do not apply if the author is in the Default team.
- Object-level permission checks are enforced.

## Blog Posts
Each post includes:
- Author (automatically set from logged-in user)
- Title
- Content
- Excerpt (first 200 characters)
- Created and updated timestamps
- Read permissions
- Write permissions

## API Endpoints

### Authentication
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/users/register/` | Register a new user |
| `POST` | `/api/users/login/` | User login (Sets Session Cookie) |
| `POST` | `/api/users/logout/` | User logout |

### Posts
* `GET /api/posts/`
* `POST /api/posts/`
* `GET /api/posts/{id}/`
* `PUT /api/posts/{id}/`
* `PATCH /api/posts/{id}/`
* `DELETE /api/posts/{id}/`

> **Note:** The list endpoint returns only accessible posts. Detail endpoints return **404** if the user lacks read access. Pagination is set to **10 posts per page**.

### Comments & Likes
* **Comments:** `GET/POST` at `/api/posts/{id}/comments/`. Only users with read access can comment.
* **Likes:** `POST` at `/api/posts/{id}/likes/`. Restricted to one like per user per post.

---

## 🛠 Tech Stack & Database
* **Stack:** Python 3.12.3, Django 6.0, Django REST Framework, PostgreSQL.
* **Testing:** `pytest` / `pytest-django`. Covers models, permissions, and complex edge cases.
* **Database Rules:** * Cascade deletions enforced for all related content.
    * Unique constraints on likes to prevent duplicates.

---

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   ```
2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies & apply migrations:**
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   ```
4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   
## API Documentation
The API is fully documented and interactive using drf-spectacular:
Schema (OpenAPI 3.0): /api/schema/
Swagger UI: /api/docs/

## Author
Luisa Fernanda Alvarez Villa
