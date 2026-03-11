-- Library Management System Database Schema
-- Create database
CREATE DATABASE IF NOT EXISTS library_management;
USE library_management;

-- Members table
CREATE TABLE IF NOT EXISTS members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    address TEXT,
    membership_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Books table
CREATE TABLE IF NOT EXISTS books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    publisher VARCHAR(100),
    publication_year YEAR,
    category VARCHAR(50),
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    shelf_location VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Borrowings table
CREATE TABLE IF NOT EXISTS borrowings (
    borrowing_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    book_id INT NOT NULL,
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE NULL,
    is_returned BOOLEAN DEFAULT FALSE,
    renewal_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- Fines table
CREATE TABLE IF NOT EXISTS fines (
    fine_id INT AUTO_INCREMENT PRIMARY KEY,
    borrowing_id INT NOT NULL,
    member_id INT NOT NULL,
    fine_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    fine_reason VARCHAR(100) NOT NULL,
    fine_date DATE NOT NULL,
    is_paid BOOLEAN DEFAULT FALSE,
    payment_date DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (borrowing_id) REFERENCES borrowings(borrowing_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
);

-- Reservations table (for future book reservations)
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    book_id INT NOT NULL,
    reservation_date DATE NOT NULL,
    status ENUM('active', 'fulfilled', 'cancelled') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_members_username ON members(username);
CREATE INDEX idx_members_email ON members(email);
CREATE INDEX idx_books_isbn ON books(isbn);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_borrowings_member_id ON borrowings(member_id);
CREATE INDEX idx_borrowings_book_id ON borrowings(book_id);
CREATE INDEX idx_borrowings_due_date ON borrowings(due_date);
CREATE INDEX idx_borrowings_is_returned ON borrowings(is_returned);
CREATE INDEX idx_fines_member_id ON fines(member_id);
CREATE INDEX idx_fines_is_paid ON fines(is_paid);

-- Insert sample data
INSERT INTO members (username, password, first_name, last_name, email, phone, address, membership_date) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8xOvzZQK6u', 'Admin', 'User', 'admin@library.com', '1234567890', '123 Library St', CURDATE()),
('john_doe', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8xOvzZQK6u', 'John', 'Doe', 'john@email.com', '9876543210', '456 Main St', CURDATE()),
('jane_smith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8xOvzZQK6u', 'Jane', 'Smith', 'jane@email.com', '5555555555', '789 Oak Ave', CURDATE());

INSERT INTO books (isbn, title, author, publisher, publication_year, category, total_copies, available_copies, shelf_location) VALUES
('978-0-13-110362-7', 'The C Programming Language', 'Brian Kernighan, Dennis Ritchie', 'Prentice Hall', 1988, 'Programming', 3, 3, 'A1-001'),
('978-0-321-35668-0', 'Effective Java', 'Joshua Bloch', 'Addison-Wesley', 2008, 'Programming', 2, 2, 'A1-002'),
('978-0-596-52068-7', 'JavaScript: The Good Parts', 'Douglas Crockford', 'O\'Reilly Media', 2008, 'Programming', 2, 2, 'A1-003'),
('978-1-449-31884-0', 'Learning Python', 'Mark Lutz', 'O\'Reilly Media', 2013, 'Programming', 4, 4, 'A1-004'),
('978-0-134-85991-9', 'Clean Code', 'Robert C. Martin', 'Prentice Hall', 2008, 'Programming', 3, 3, 'A1-005');

