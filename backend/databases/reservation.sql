-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Mar 21, 2025 at 09:43 AM
-- Server version: 8.2.0
-- PHP Version: 8.2.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `reservation`
--

-- --------------------------------------------------------

--
-- Table structure for table `reservation`
--

DROP TABLE IF EXISTS `reservation`;
CREATE TABLE IF NOT EXISTS `reservation` (
  `reservation_id` int NOT NULL AUTO_INCREMENT,
  `restaurant_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `table_no` int DEFAULT NULL,
  `status` varchar(999) NOT NULL,
  `count` int DEFAULT '10',
  `price` double DEFAULT NULL,
  `time` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`reservation_id`),
  KEY `restaurant_id` (`restaurant_id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `reservation`
--

INSERT INTO `reservation` (`reservation_id`, `restaurant_id`, `user_id`, `table_no`, `status`, `count`, `price`, `time`) VALUES
(1, 1, 1, 5, 'Booked', 2, 45.99, '2025-03-13 11:28:31'),
(2, 2, 2, 3, 'Booked', 4, 78.5, '2025-03-14 11:28:31'),
(3, 3, 3, 12, 'Booked', 3, 99.99, '2025-03-15 11:28:31'),
(4, 4, 4, 12, 'Booked', 2, 15.36, '2025-03-16 11:28:31'),
(5, 5, 5, 7, 'Booked', 2, 27.89, '2025-03-17 11:28:31'),
(6, 6, 6, 9, 'Booked', 3, 65.75, '2025-03-18 11:28:31');

-- --------------------------------------------------------

--
-- Table structure for table `restaurant`
--

DROP TABLE IF EXISTS `restaurant`;
CREATE TABLE IF NOT EXISTS `restaurant` (
  `restaurant_id` int NOT NULL AUTO_INCREMENT,
  `capacity` int NOT NULL,
  `availability` tinyint(1) NOT NULL,
  `name` varchar(30) NOT NULL,
  `address` varchar(999) NOT NULL,
  `rating` varchar(999) NOT NULL,
  `cuisine` varchar(999) NOT NULL,
  PRIMARY KEY (`restaurant_id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `restaurant`
--

INSERT INTO `restaurant` (`restaurant_id`, `capacity`, `availability`, `name`, `address`, `rating`, `cuisine`) VALUES
(1, 50, 1, 'Ocean View Diner', '123 Seaside Lane', '4.5', 'Seafood'),
(2, 30, 1, 'Mountain Grill', '456 Highland Rd', '4.7', 'Steakhouse'),
(3, 100, 1, 'City Central Buffet', '789 Downtown Ave', '4.2', 'Buffet'),
(4, 25, 0, 'Hidden Sushi Spot', '12 Sakura St', '4.9', 'Japanese'),
(5, 40, 1, 'Pasta Paradise', '33 Italian Blvd', '4.3', 'Italian'),
(6, 60, 0, 'BBQ Pit Masters', '55 Smokehouse Lane', '4.6', 'Barbecue');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(999) NOT NULL,
  `phoneNo` int NOT NULL,
  `homeAddress` varchar(100) NOT NULL,
  `postalCode` int NOT NULL,
  `email` varchar(999) NOT NULL,
  `password` varchar(999) NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`user_id`, `name`, `phoneNo`, `homeAddress`, `postalCode`, `email`, `password`) VALUES
(1, 'KS', 91838796, '123 Maple Street', 456789, 'ks.quek.2023@smu.edu.sg', '000000'),
(2, 'Bob Smith', 87654321, '456 Elm Avenue', 123456, 'bob.smith@example.com', 'bobSecure456'),
(3, 'Charlie Lee', 81239876, '789 Oak Drive', 654321, 'charlie.lee@example.com', 'charliePass789'),
(4, 'Diana Ross', 92345678, '321 Pine Lane', 112233, 'diana.ross@example.com', 'dianaRockz2024'),
(5, 'Evan Wright', 83456789, '654 Birch Court', 334455, 'evan.w@example.com', 'evanStrongPass'),
(6, 'Fiona Green', 84561234, '987 Willow Way', 778899, 'fiona.green@example.com', 'fiona789secure');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
