-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jan 27, 2023 at 11:15 AM
-- Server version: 10.3.37-MariaDB-0ubuntu0.20.04.1
-- PHP Version: 7.4.3-4ubuntu2.17

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `niko_db7`
--
CREATE DATABASE IF NOT EXISTS `DB-Name` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `DB-Name`;

-- --------------------------------------------------------

--
-- Table structure for table `mentions`
--

CREATE TABLE `mentions` (
  `tweet_id` bigint(255) NOT NULL,
  `author_id` bigint(255) NOT NULL,
  `author_username` varchar(255) NOT NULL,
  `tweet_text` varchar(1000) NOT NULL,
  `retweet_id` bigint(255) DEFAULT NULL,
  `reply_id` bigint(255) DEFAULT NULL,
  `quote_id` bigint(255) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `attachment1` varchar(255) DEFAULT NULL,
  `attachment2` varchar(255) DEFAULT NULL,
  `attachment3` varchar(255) DEFAULT NULL,
  `attachment4` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `toot_id` bigint(255) NOT NULL,
  `notification_type` varchar(255) NOT NULL,
  `replied_id` bigint(255) DEFAULT NULL,
  `timestamp` timestamp(6) NOT NULL DEFAULT current_timestamp(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tweets`
--

CREATE TABLE `tweets` (
  `tweet_id` bigint(255) NOT NULL,
  `author_id` bigint(255) NOT NULL,
  `author_username` varchar(255) NOT NULL,
  `tweet_text` varchar(1000) NOT NULL,
  `retweet_id` bigint(255) DEFAULT NULL,
  `reply_id` bigint(255) DEFAULT NULL,
  `quote_id` bigint(255) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `attachment1` varchar(255) DEFAULT NULL,
  `attachment2` varchar(255) DEFAULT NULL,
  `attachment3` varchar(255) DEFAULT NULL,
  `attachment4` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `twoot_ids`
--

CREATE TABLE `twoot_ids` (
  `tweet_id` bigint(255) NOT NULL,
  `toot_id` bigint(255) NOT NULL,
  `time` timestamp(6) NOT NULL DEFAULT current_timestamp(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `twoot_mentions`
--

CREATE TABLE `twoot_mentions` (
  `tweet_id` bigint(255) NOT NULL,
  `toot_id` bigint(255) NOT NULL,
  `time` timestamp(6) NOT NULL DEFAULT current_timestamp(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `mentions`
--
ALTER TABLE `mentions`
  ADD PRIMARY KEY (`tweet_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`toot_id`,`timestamp`);

--
-- Indexes for table `tweets`
--
ALTER TABLE `tweets`
  ADD PRIMARY KEY (`tweet_id`);

--
-- Indexes for table `twoot_ids`
--
ALTER TABLE `twoot_ids`
  ADD PRIMARY KEY (`tweet_id`),
  ADD UNIQUE KEY `toot_id` (`toot_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
