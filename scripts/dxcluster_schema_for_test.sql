-------------------------------------------------------------
-- script for creating a test database
-------------------------------------------------------------

drop database IF EXISTS dxcluster;
create database dxcluster;

grant all privileges on dxcluster.* to webdb@localhost identified by 'pswd';

use dxcluster;

-- MySQL dump 10.16  Distrib 10.1.48-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: dxcluster
-- ------------------------------------------------------
-- Server version       10.1.48-MariaDB-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `spot`
--

DROP TABLE IF EXISTS `spot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `spot` (
  `rowid` int(11) NOT NULL AUTO_INCREMENT,
  `freq` double NOT NULL,
  `spotcall` varchar(14) NOT NULL,
  `time` int(11) NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  `spotter` varchar(14) NOT NULL,
  `spotdxcc` smallint(6) DEFAULT NULL,
  `spotterdxcc` smallint(6) DEFAULT NULL,
  `origin` varchar(14) DEFAULT NULL,
  `spotitu` tinyint(4) DEFAULT NULL,
  `spotcq` tinyint(4) DEFAULT NULL,
  `spotteritu` tinyint(4) DEFAULT NULL,
  `spottercq` tinyint(4) DEFAULT NULL,
  `spotstate` char(2) DEFAULT NULL,
  `spotterstate` char(2) DEFAULT NULL,
  `ipaddr` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`rowid`),
  KEY `spot_ix1` (`time`),
  KEY `spot_ix2` (`spotcall`),
  KEY `spiderweb_spotter` (`spotter`)
) ENGINE=InnoDB AUTO_INCREMENT=9283036 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

---INSERT INTO `spot` VALUES (1,18123,'IU1BOX',1578091140,NULL,'IU1BOW',85,85,'IU1BOW-2',28,15,28,15,NULL,NULL,'5.198.229.129');
---INSERT INTO `spot` VALUES (1,18123,'IU1BOX',UNIX_TIMESTAMP(),NULL,'IU1BOW',85,85,'IU1BOW-2',28,15,28,15,NULL,NULL,'5.198.229.129');

