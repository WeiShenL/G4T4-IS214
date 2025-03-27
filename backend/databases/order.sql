-- SQL Schema for Order Microservice
CREATE DATABASE IF NOT EXISTS `order`;
USE `order`;

CREATE TABLE IF NOT EXISTS `menu` (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_ID VARCHAR(13) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    price DECIMAL(10, 2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS `order_table` (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS `order_item` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL
);
