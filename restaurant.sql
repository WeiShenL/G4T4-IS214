-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jan 14, 2019 at 06:42 AM
-- Server version: 5.7.19
-- PHP Version: 7.1.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
CREATE DATABASE IF NOT EXISTS `restaurant_db` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `restaurant_db`;
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Restaurants (
    restaurant_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Tables (
    table_id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES Restaurants(restaurant_id) ON DELETE CASCADE,
    table_number VARCHAR(10) NOT NULL,
    capacity INT NOT NULL
);

CREATE TABLE Bookings (
    booking_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    restaurant_id INT REFERENCES Restaurants(restaurant_id) ON DELETE CASCADE,
    table_id INT REFERENCES Tables(table_id) ON DELETE SET NULL,
    booking_time TIMESTAMP NOT NULL,
    status VARCHAR(50) CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Packages (
    package_id SERIAL PRIMARY KEY,
    restaurant_id INT REFERENCES Restaurants(restaurant_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    booking_id INT REFERENCES Bookings(booking_id) ON DELETE CASCADE,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    order_type VARCHAR(50) CHECK (order_type IN ('dine-in', 'delivery')) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) CHECK (status IN ('pending', 'paid', 'cancelled', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Order_Items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES Orders(order_id) ON DELETE CASCADE,
    package_id INT REFERENCES Packages(package_id) ON DELETE CASCADE,
    quantity INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

CREATE TABLE Payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES Orders(order_id) ON DELETE CASCADE,
    stripe_payment_id VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) CHECK (status IN ('pending', 'successful', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Deliveries (
    delivery_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES Orders(order_id) ON DELETE CASCADE,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    delivery_address TEXT NOT NULL,
    delivery_time TIMESTAMP NOT NULL,
    status VARCHAR(50) CHECK (status IN ('pending', 'dispatched', 'delivered', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Sample Data
INSERT INTO Users (name, email, phone, password_hash) VALUES
('Alice Johnson', 'alice@example.com', '1234567890', 'hashed_pw1'),
('Bob Smith', 'bob@example.com', '1234567891', 'hashed_pw2'),
('Charlie Brown', 'charlie@example.com', '1234567892', 'hashed_pw3'),
('David Wilson', 'david@example.com', '1234567893', 'hashed_pw4'),
('Emma Watson', 'emma@example.com', '1234567894', 'hashed_pw5');

INSERT INTO Restaurants (name, location, latitude, longitude, phone, email) VALUES
('Gourmet Dine', '123 Main St', 40.712776, -74.005974, '9876543210', 'gourmet@example.com'),
('Seafood Haven', '456 Ocean Ave', 34.052235, -118.243683, '9876543211', 'seafood@example.com');

INSERT INTO Tables (restaurant_id, table_number, capacity) VALUES
(1, 'T1', 4), (1, 'T2', 2), (2, 'T1', 6);

INSERT INTO Packages (restaurant_id, name, description, price) VALUES
(1, 'Romantic Dinner', 'A special dinner for two with wine pairing', 79.99),
(2, 'Family Feast', 'A meal package for a family of four', 119.99);

INSERT INTO Bookings (user_id, restaurant_id, table_id, booking_time, status) VALUES
(1, 1, 1, '2025-04-01 19:00:00', 'confirmed'),
(2, 2, 3, '2025-04-02 20:00:00', 'pending');

INSERT INTO Orders (booking_id, user_id, order_type, total_amount, status) VALUES
(1, 1, 'dine-in', 79.99, 'paid'),
(2, 2, 'dine-in', 119.99, 'pending');

INSERT INTO Order_Items (order_id, package_id, quantity, subtotal) VALUES
(1, 1, 1, 79.99),
(2, 2, 1, 119.99);

INSERT INTO Payments (order_id, stripe_payment_id, amount, status) VALUES
(1, 'pi_12345', 79.99, 'successful');


