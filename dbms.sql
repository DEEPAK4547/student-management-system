-- Student Management System Database Schema
-- Run this in MySQL before starting the server

CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role ENUM('admin', 'student') DEFAULT 'admin'
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    roll_no VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(50) NOT NULL,
    year INT NOT NULL CHECK (year BETWEEN 1 AND 4),
    cgpa DECIMAL(3,2) CHECK (cgpa BETWEEN 0.00 AND 10.00),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin');

-- Insert sample student data
INSERT INTO students (roll_no, name, email, phone, department, year, cgpa) VALUES
('R101', 'Alice Johnson', 'alice@univ.edu', '9876543210', 'Computer Science', 3, 8.50),
('R102', 'Bob Smith', 'bob@univ.edu', '9876543211', 'Electrical', 2, 7.80),
('R103', 'Charlie Brown', 'charlie@univ.edu', '9876543212', 'Mechanical', 4, 9.10),
('R104', 'Diana Prince', 'diana@univ.edu', '9876543213', 'Computer Science', 1, 8.90),
('R105', 'Evan Wright', 'evan@univ.edu', '9876543214', 'Civil', 3, 7.20);

