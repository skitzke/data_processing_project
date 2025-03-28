# Data Processing Project

## Overview
This is a FastAPI-based project that provides a REST API for user authentication, data management, and visualization. It supports CRUD operations for users and data entries, authentication with JWT tokens, and exports data in both JSON and CSV formats. Additionally, it includes a role-based access system with admin capabilities and a visualization feature using Matplotlib.

---

## Features
- **User Authentication** (Register, Login, JWT Token-based Authentication)
- **Role-Based Access Control** (User & Admin)
- **CRUD Operations for Users & Data**
- **Data Export in JSON & CSV Formats**
- **Graph Visualization of User Roles**
- **Admin Privileges** to promote users and manage data
- **Unit Testing with Pytest**

---

## Prerequisites
Ensure you have the following installed:

- Python 3.9+
- PostgreSQL
- Virtual Environment (venv)
- `pip` package manager

---

## Setup Instructions
### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/data_processing_project.git
cd data_processing_project
```

### 2. Create a Virtual Environment & Activate It
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and set the following values:
```
DATABASE_URL=postgresql://username:password@localhost:5432/dataprocessing
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Set Up Database & Migrations
```bash
alembic upgrade head
```

---

## Running the Application
### Start the FastAPI Server
```bash
uvicorn app.main:app --reload
```

The API will be accessible at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

To view API documentation:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---
### * Please note:
If the local port 8000 does not load, it means there is a conflict in ports, therefore use this command instead:
```bash
uvicorn app.main:app --reload --port 8080
```
This means the new API accessible link will be at: [http://127.0.0.1:8080](http://127.0.0.1:8080)

API documentation:
- Swagger UI: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
- Redoc: [http://127.0.0.1:8080/redoc](http://127.0.0.1:8080/redoc)

## API Endpoints
### **Authentication**
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Authenticate and get a JWT token |

### **Users**
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/users/` | Get all users (JSON or CSV) |
| GET | `/users/{user_id}` | Get a specific user by ID |
| PUT | `/users/{user_id}` | Update user details (Admin required) |
| DELETE | `/users/{user_id}` | Delete a user (Admin required) |
| GET | `/users/roles-chart` | Get a bar chart of user roles |
| PUT | `/users/promote/{user_id}` | Promote a user to admin (Admin required) |

### **Data Entries**
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/data/` | Create a new data entry |
| GET | `/data/` | Get all data entries |
| GET | `/data/{data_id}` | Get a specific data entry |
| PUT | `/data/{data_id}` | Update a data entry |
| DELETE | `/data/{data_id}` | Delete a data entry |

---

## Admin Setup
### **Manually Create an Admin in PostgreSQL**
```sql
INSERT INTO users (username, hashed_password, role) VALUES ('admin_user', '<hashed_password>', 'admin');
```
To generate a hashed password:
```python
from app.utils import get_password_hash
print(get_password_hash("your_secure_password"))
```

### **Promote an Existing User to Admin**
```sql
UPDATE users SET role = 'admin' WHERE username = 'existing_user';
```
Or use the API:
```bash
PUT /users/promote/{user_id}
```

---

## Running Tests
To run the tests, execute:
```bash
pytest tests/
```
Or if you're using Intellij, execute this in the test env terminal first:
```bash
pip install httpx
```
Then you'll be able to run the tests directly from the file using the play icon next to each test.

---

## Visualization

![Visualization](https://i.imgur.com/QjaUCK2.png)

1. To see the visualization, create users and admins so that the database has data.
2. On the top right of the image there is a lock button, press it to authenticate as a user or admin.
3. Once Authenticated, press execute and the chat will appear according to the data in the database.