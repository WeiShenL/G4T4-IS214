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

-- Restaurant table
CREATE TABLE IF NOT EXISTS `restaurant` (
    `restaurant_id` char(13) NOT NULL,
    `name` varchar(64) NOT NULL,
    `cuisine` varchar(64) NOT NULL,
    `rating` decimal(2,1) NOT NULL,
    `price_range` varchar(5) NOT NULL,
    `meal_packages` text DEFAULT NULL,
    `location_name` varchar(128) DEFAULT NULL,
    `location_coordinates` varchar(64) DEFAULT NULL,
    PRIMARY KEY (`restaurant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Reservation table
DROP TABLE IF EXISTS `reservation`;
CREATE TABLE IF NOT EXISTS `reservation` (
    `reservation_id` int(11) NOT NULL AUTO_INCREMENT,
    `restaurant_id` char(13) NOT NULL,
    `customer_name` varchar(64) NOT NULL,
    `reservation_date` date NOT NULL,
    `reservation_time` time NOT NULL,
    `party_size` int(11) NOT NULL,
    PRIMARY KEY (`reservation_id`),
    FOREIGN KEY (`restaurant_id`) REFERENCES `restaurant`(`restaurant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Sample data for restaurants
INSERT INTO `restaurant` (`restaurant_id`, `name`, `cuisine`, `rating`, `price_range`, `meal_packages`, `location_name`, `location_coordinates`) VALUES
('RES0012345678', 'The Gourmet Corner', 'French', 4.5, '$$$$', 'Parisian Delight: Croissant, Quiche, Coffee; French Feast: Coq au Vin, Ratatouille, Crème Brûlée', 'Paris Center', '48.8566,2.3522'),
('RES0098765432', 'Tokyo Sushi Master', 'Japanese', 4.8, '$$$', 'Sushi Lover: Assorted Sushi, Miso Soup, Green Tea; Bento Box: Teriyaki Chicken, Rice, Tempura, Salad', 'Shibuya', '35.6895,139.6917'),
('RES0055512345', 'Mama Mia Pizzeria', 'Italian', 4.3, '$$', 'Pizza Party: Margherita Pizza, Garlic Bread, Tiramisu; Pasta Perfection: Spaghetti Carbonara, Caesar Salad, Panna Cotta', 'Rome Downtown', '41.9028,12.4964');

-- Sample data for reservations
INSERT INTO `reservation` (`restaurant_id`, `customer_name`, `reservation_date`, `reservation_time`, `party_size`) VALUES
('RES0012345678', 'John Doe', '2025-03-25', '19:00:00', 2),
('RES0098765432', 'Jane Smith', '2025-03-26', '20:30:00', 4),
('RES0055512345', 'Bob Johnson', '2025-03-27', '18:15:00', 3);

COMMIT;
