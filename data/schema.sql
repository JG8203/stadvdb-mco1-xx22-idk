/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.5.2-MariaDB, for osx10.19 (arm64)
--
-- Host: stadvb.chsuys826h4e.ap-southeast-2.rds.amazonaws.com    Database: games
-- ------------------------------------------------------
-- Server version	10.11.9-MariaDB-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `Bridge_Game_Category`
--

DROP TABLE IF EXISTS `Bridge_Game_Category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Bridge_Game_Category` (
  `GameID_id` int(11) NOT NULL,
  `CategoryID_id` int(11) NOT NULL,
  UNIQUE KEY `bridgegamecategory_GameID_id_CategoryID_id` (`GameID_id`,`CategoryID_id`),
  KEY `bridgegamecategory_GameID_id` (`GameID_id`),
  KEY `bridgegamecategory_CategoryID_id` (`CategoryID_id`),
  CONSTRAINT `bridge_game_category_ibfk_1` FOREIGN KEY (`GameID_id`) REFERENCES `Dim_Game` (`GameID`) ON DELETE CASCADE,
  CONSTRAINT `bridge_game_category_ibfk_2` FOREIGN KEY (`CategoryID_id`) REFERENCES `Dim_Category` (`CategoryID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Bridge_Game_Developer`
--

DROP TABLE IF EXISTS `Bridge_Game_Developer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Bridge_Game_Developer` (
  `GameID_id` int(11) NOT NULL,
  `DeveloperID_id` int(11) NOT NULL,
  UNIQUE KEY `bridgegamedeveloper_GameID_id_DeveloperID_id` (`GameID_id`,`DeveloperID_id`),
  KEY `bridgegamedeveloper_GameID_id` (`GameID_id`),
  KEY `bridgegamedeveloper_DeveloperID_id` (`DeveloperID_id`),
  CONSTRAINT `bridge_game_developer_ibfk_1` FOREIGN KEY (`GameID_id`) REFERENCES `Dim_Game` (`GameID`) ON DELETE CASCADE,
  CONSTRAINT `bridge_game_developer_ibfk_2` FOREIGN KEY (`DeveloperID_id`) REFERENCES `Dim_Developer` (`DeveloperID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Bridge_Game_Genre`
--

DROP TABLE IF EXISTS `Bridge_Game_Genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Bridge_Game_Genre` (
  `GameID_id` int(11) NOT NULL,
  `GenreID_id` int(11) NOT NULL,
  UNIQUE KEY `bridgegamegenre_GameID_id_GenreID_id` (`GameID_id`,`GenreID_id`),
  KEY `bridgegamegenre_GameID_id` (`GameID_id`),
  KEY `bridgegamegenre_GenreID_id` (`GenreID_id`),
  CONSTRAINT `bridge_game_genre_ibfk_1` FOREIGN KEY (`GameID_id`) REFERENCES `Dim_Game` (`GameID`) ON DELETE CASCADE,
  CONSTRAINT `bridge_game_genre_ibfk_2` FOREIGN KEY (`GenreID_id`) REFERENCES `Dim_Genre` (`GenreID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Bridge_Game_Language`
--

DROP TABLE IF EXISTS `Bridge_Game_Language`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Bridge_Game_Language` (
  `GameID_id` int(11) NOT NULL,
  `LanguageID_id` int(11) NOT NULL,
  UNIQUE KEY `bridgegamelanguage_GameID_id_LanguageID_id` (`GameID_id`,`LanguageID_id`),
  KEY `bridgegamelanguage_GameID_id` (`GameID_id`),
  KEY `bridgegamelanguage_LanguageID_id` (`LanguageID_id`),
  CONSTRAINT `bridge_game_language_ibfk_1` FOREIGN KEY (`GameID_id`) REFERENCES `Dim_Game` (`GameID`) ON DELETE CASCADE,
  CONSTRAINT `bridge_game_language_ibfk_2` FOREIGN KEY (`LanguageID_id`) REFERENCES `Dim_Language` (`LanguageID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Bridge_Game_Publisher`
--

DROP TABLE IF EXISTS `Bridge_Game_Publisher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Bridge_Game_Publisher` (
  `GameID_id` int(11) NOT NULL,
  `PublisherID_id` int(11) NOT NULL,
  UNIQUE KEY `bridgegamepublisher_GameID_id_PublisherID_id` (`GameID_id`,`PublisherID_id`),
  KEY `bridgegamepublisher_GameID_id` (`GameID_id`),
  KEY `bridgegamepublisher_PublisherID_id` (`PublisherID_id`),
  CONSTRAINT `bridge_game_publisher_ibfk_1` FOREIGN KEY (`GameID_id`) REFERENCES `Dim_Game` (`GameID`) ON DELETE CASCADE,
  CONSTRAINT `bridge_game_publisher_ibfk_2` FOREIGN KEY (`PublisherID_id`) REFERENCES `Dim_Publisher` (`PublisherID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Bridge_Game_Tag`
--

DROP TABLE IF EXISTS `Bridge_Game_Tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Bridge_Game_Tag` (
  `GameID_id` int(11) NOT NULL,
  `TagID_id` int(11) NOT NULL,
  UNIQUE KEY `bridgegametag_GameID_id_TagID_id` (`GameID_id`,`TagID_id`),
  KEY `bridgegametag_GameID_id` (`GameID_id`),
  KEY `bridgegametag_TagID_id` (`TagID_id`),
  CONSTRAINT `bridge_game_tag_ibfk_1` FOREIGN KEY (`GameID_id`) REFERENCES `Dim_Game` (`GameID`) ON DELETE CASCADE,
  CONSTRAINT `bridge_game_tag_ibfk_2` FOREIGN KEY (`TagID_id`) REFERENCES `Dim_Tag` (`TagID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Dim_Category`
--

DROP TABLE IF EXISTS `Dim_Category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Dim_Category` (
  `CategoryID` int(11) NOT NULL AUTO_INCREMENT,
  `CategoryName` varchar(255) NOT NULL,
  PRIMARY KEY (`CategoryID`),
  UNIQUE KEY `dimcategory_CategoryName` (`CategoryName`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Dim_Developer`
--

DROP TABLE IF EXISTS `Dim_Developer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Dim_Developer` (
  `DeveloperID` int(11) NOT NULL AUTO_INCREMENT,
  `DeveloperName` varchar(255) NOT NULL,
  PRIMARY KEY (`DeveloperID`),
  UNIQUE KEY `dimdeveloper_DeveloperName` (`DeveloperName`)
) ENGINE=InnoDB AUTO_INCREMENT=59690 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Dim_Game`
--

DROP TABLE IF EXISTS `Dim_Game`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Dim_Game` (
  `GameID` int(11) NOT NULL AUTO_INCREMENT,
  `AppID` int(11) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `ReleaseDate` date DEFAULT NULL,
  `RequiredAge` int(11) DEFAULT NULL,
  `AboutGame` text DEFAULT NULL,
  `Website` varchar(255) DEFAULT NULL,
  `SupportURL` varchar(255) DEFAULT NULL,
  `SupportEmail` varchar(255) DEFAULT NULL,
  `HeaderImage` varchar(255) DEFAULT NULL,
  `Notes` text DEFAULT NULL,
  PRIMARY KEY (`GameID`),
  UNIQUE KEY `dimgame_AppID` (`AppID`)
) ENGINE=InnoDB AUTO_INCREMENT=97411 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Dim_Genre`
--

DROP TABLE IF EXISTS `Dim_Genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Dim_Genre` (
  `GenreID` int(11) NOT NULL AUTO_INCREMENT,
  `GenreName` varchar(255) NOT NULL,
  PRIMARY KEY (`GenreID`),
  UNIQUE KEY `dimgenre_GenreName` (`GenreName`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Dim_Language`
--

DROP TABLE IF EXISTS `Dim_Language`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Dim_Language` (
  `LanguageID` int(11) NOT NULL AUTO_INCREMENT,
  `LanguageName` varchar(255) NOT NULL,
  PRIMARY KEY (`LanguageID`),
  UNIQUE KEY `dimlanguage_LanguageName` (`LanguageName`)
) ENGINE=InnoDB AUTO_INCREMENT=132 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Dim_Publisher`
--

DROP TABLE IF EXISTS `Dim_Publisher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Dim_Publisher` (
  `PublisherID` int(11) NOT NULL AUTO_INCREMENT,
  `PublisherName` varchar(255) NOT NULL,
  PRIMARY KEY (`PublisherID`),
  UNIQUE KEY `dimpublisher_PublisherName` (`PublisherName`)
) ENGINE=InnoDB AUTO_INCREMENT=49339 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Dim_Tag`
--

DROP TABLE IF EXISTS `Dim_Tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Dim_Tag` (
  `TagID` int(11) NOT NULL AUTO_INCREMENT,
  `TagName` varchar(255) NOT NULL,
  PRIMARY KEY (`TagID`),
  UNIQUE KEY `dimtag_TagName` (`TagName`)
) ENGINE=InnoDB AUTO_INCREMENT=453 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Dim_Time`
--

DROP TABLE IF EXISTS `Dim_Time`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Dim_Time` (
  `DateID` int(11) NOT NULL,
  `ReleaseDate` date NOT NULL,
  `Year` int(11) NOT NULL,
  `Quarter` int(11) NOT NULL,
  `Month` int(11) NOT NULL,
  `Day` int(11) NOT NULL,
  `Weekday` varchar(255) NOT NULL,
  PRIMARY KEY (`DateID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Fact_GameMetrics`
--

DROP TABLE IF EXISTS `Fact_GameMetrics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Fact_GameMetrics` (
  `FactID` int(11) NOT NULL AUTO_INCREMENT,
  `GameID_id` int(11) NOT NULL,
  `Price` decimal(10,2) DEFAULT NULL,
  `EstimatedOwners` int(11) DEFAULT NULL,
  `PeakCCU` int(11) DEFAULT NULL,
  `AvgPlaytimeForever` int(11) DEFAULT NULL,
  `AvgPlaytimeTwoWeeks` int(11) DEFAULT NULL,
  `MedianPlaytimeForever` int(11) DEFAULT NULL,
  `MedianPlaytimeTwoWeeks` int(11) DEFAULT NULL,
  `PositiveReviews` int(11) DEFAULT NULL,
  `NegativeReviews` int(11) DEFAULT NULL,
  `MetacriticScore` int(11) DEFAULT NULL,
  `UserScore` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`FactID`),
  KEY `factgamemetrics_GameID_id` (`GameID_id`),
  CONSTRAINT `fact_gamemetrics_ibfk_1` FOREIGN KEY (`GameID_id`) REFERENCES `Dim_Game` (`GameID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=97411 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2024-10-23 16:45:59
