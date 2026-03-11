# How to Run the Library Management System Project

Follow these step-by-step instructions to get the entire project (Frontend, Backend, and Database) running successfully on your local machine.

## Prerequisites
Before starting, ensure you have the following installed on your system:
1. **Python 3.8+** (Make sure Python is added to your system PATH)
2. **MySQL Server** (Make sure it is running and accessible)
3. **Git Bash** or a terminal of your choice

---

## Step 1: Database Setup
The robust application requires a MySQL database to store books, members, and borrowings.

1. Open your terminal or command prompt.
2. Log in to your MySQL server as root:
   ```bash
   mysql -u root -p
   ```
   *(Enter your MySQL root password when prompted)*
3. Create the database:
   ```sql
   CREATE DATABASE IF NOT EXISTS library_management DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```
4. Import the database schema and sample data:
   Navigate to the project directory (`c:\Users\sujal\Downloads\Library Management System Project`) and run:
   ```bash
   mysql -u root -p library_management < schema.sql
   ```
   *(Enter your MySQL root password when prompted)*

---

## Step 2: Configure Environment Variables
The project uses a `.env` file to connect to the database.

1. Open the `.env` file in the project folder.
2. Ensure the `MYSQL_PASSWORD` matches your local MySQL root password.
   ```env
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password_here
   MYSQL_DATABASE=library_management
   
   JWT_SECRET_KEY=jwt-secret-string-for-library-management
   SECRET_KEY=asdf#FGSgvasgf$5$WGT
   ```

---

## Step 3: Python Backend Setup
The backend is built with Flask, and it also serves the compiled frontend.

1. Open a terminal in the project directory (`c:\Users\sujal\Downloads\Library Management System Project`).
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - **Windows:**
     ```bash
     .\venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```
4. Install all the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Step 4: Run the Application!
Now that the database and dependencies are set up, you can start the application! The Flask backend will also serve the static frontend files.

1. First, make sure your virtual environment is activated (from Step 3).
2. Start the application:
   ```bash
   python src/main.py
   ```
3. You should see an output in the terminal indicating that the Flask app is running (e.g., `* Running on all addresses (0.0.0.0)`).

---

## Step 5: Access the System
Open your favorite web browser and navigate to:
**👉 http://localhost:5000/**

You will be greeted by the Library Management System login screen!

### Valid Test Credentials
Sample users were created during Step 1 when `schema.sql` was imported. You can use these to test the app:

**Admin User:**
- Username: `admin`
- Password: `password`

**Regular Members:**
- Username: `john_doe` / Password: `password`
- Username: `jane_smith` / Password: `password`

## Troubleshooting
- **Database Connection Error**: Double check your `MYSQL_PASSWORD` in the `.env` file.
- **Port 5000 already in use**: If another program is using port 5000, stop it, or edit the `port=5000` argument in `src/main.py` at the bottom of the file to a different port (e.g., 5001).
