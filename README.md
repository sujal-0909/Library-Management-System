📚 Library Management System

A **Library Management System** built using **Python, Flask, and MySQL** that allows libraries to manage books, members, borrowing operations, fines, and reports efficiently through REST APIs and a simple frontend interface.

This project demonstrates **backend API development, database design, and system architecture** for managing a digital library.

---

🚀 Features

📖 Book Management

* Add new books to the library
* Update book details
* Delete books
* Search books by title or author

👥 Member Management

* Register new members
* Manage member records
* Track borrowing activity

🔄 Borrowing System

* Borrow books
* Return books
* Track borrowing history

💰 Fine Management

* Automatic fine calculation
* Grace period handling
* Fine tracking

📊 Reports

* Library usage statistics
* Borrowed books tracking
* Member activity reports

🔎 Search Functionality

* Search books using keywords

---

🛠️ Tech Stack

**Backend**

* Python
* Flask

**Database**

* MySQL

**Frontend**

* HTML
* CSS
* JavaScript

**Testing**

* Pytest

**Tools**

* Postman
* Git & GitHub

---

📁 Project Structure

```
Library-Management-System/
│
├── src/
│   ├── main.py
│   ├── config.py
│   │
│   ├── models/
│   │   ├── book.py
│   │   ├── borrowing.py
│   │   ├── fine.py
│   │   ├── member.py
│   │   └── reservation.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── borrowings.py
│   │   ├── fines.py
│   │   ├── members.py
│   │   └── reports.py
│   │
│   └── static/
│       ├── index.html
│       ├── script.js
│       └── styles.css
│
├── tests/
│   ├── test_api_auth.py
│   └── test_api_books.py
│
├── schema.sql
├── requirements.txt
├── run.sh
└── README.md
```

---

⚙️ Installation & Setup

1️⃣ Clone the Repository

```
git clone https://github.com/yourusername/library-management-system.git
```

---

2️⃣ Navigate to the Project Folder

```
cd library-management-system
```

---

3️⃣ Create Virtual Environment

```
python -m venv venv
```

Activate environment:

**Windows**

```
venv\Scripts\activate
```

**Mac / Linux**

```
source venv/bin/activate
```

---

4️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

5️⃣ Setup MySQL Database

Create a database and run the SQL script:

```
schema.sql
```

This will create all required tables for the project.

---

6️⃣ Configure Database

Update database configuration in:

```
src/config.py
---

7️⃣ Run the Application

```
python src/main.py
```

The application will start at:

```
http://127.0.0.1:5000
```

---

📡 Example API Endpoints

| Method | Endpoint            | Description     |
| ------ | ------------------- | --------------- |
| POST   | `/api/books`        | Add new book    |
| GET    | `/api/books/search` | Search books    |
| POST   | `/api/borrow`       | Borrow book     |
| POST   | `/api/return`       | Return book     |
| GET    | `/api/reports`      | View statistics |

---

🧪 Running Tests

Run automated tests:

```
pytest
```

---

🔮 Future Improvements

* JWT Authentication
* Admin Dashboard
* Email Notifications
* Book Reservation System
* Docker Deployment
* Cloud Deployment

---

👨‍💻 Author

Sujal Jariwala

---

📜 License

This project is created for **educational and demonstration purposes**.
