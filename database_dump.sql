-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: student_portal_db
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity`
--

DROP TABLE IF EXISTS `activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity` (
  `activityId` int NOT NULL AUTO_INCREMENT,
  `activityName` varchar(100) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `level` varchar(30) DEFAULT NULL,
  `achievement` varchar(100) DEFAULT NULL,
  `proof_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`activityId`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity`
--

LOCK TABLES `activity` WRITE;
/*!40000 ALTER TABLE `activity` DISABLE KEYS */;
INSERT INTO `activity` VALUES (1,'Hackathon','Technical','National','Winner',NULL),(2,'hackathon','carricular',NULL,'participant',NULL),(3,'hackathon','carricular',NULL,'participant',NULL),(4,'hackathon','carricular',NULL,'participant',NULL),(10,'tech','carricular','College','participant',NULL),(11,'tech','carricular','College','participant',NULL),(12,'paper ','carricular','College','winner','act_u18_20260305_104437_22bce024_hci_prac_3.pdf');
/*!40000 ALTER TABLE `activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `userId` int NOT NULL,
  `adminLevel` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`userId`),
  CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`userId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (6,'super');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `committee`
--

DROP TABLE IF EXISTS `committee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `committee` (
  `committeeCode` int NOT NULL AUTO_INCREMENT,
  `committeeName` varchar(100) NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`committeeCode`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `committee`
--

LOCK TABLES `committee` WRITE;
/*!40000 ALTER TABLE `committee` DISABLE KEYS */;
INSERT INTO `committee` VALUES (1,'Sports Committee','Extracurricular'),(2,'Aces','tech'),(3,'Aces','tech');
/*!40000 ALTER TABLE `committee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `committeemembership`
--

DROP TABLE IF EXISTS `committeemembership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `committeemembership` (
  `membershipId` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `committeeCode` int NOT NULL,
  `role` varchar(50) DEFAULT NULL,
  `joinDate` date DEFAULT NULL,
  PRIMARY KEY (`membershipId`),
  UNIQUE KEY `userId` (`userId`,`committeeCode`),
  KEY `committeeCode` (`committeeCode`),
  CONSTRAINT `committeemembership_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`userId`),
  CONSTRAINT `committeemembership_ibfk_2` FOREIGN KEY (`committeeCode`) REFERENCES `committee` (`committeeCode`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `committeemembership`
--

LOCK TABLES `committeemembership` WRITE;
/*!40000 ALTER TABLE `committeemembership` DISABLE KEYS */;
INSERT INTO `committeemembership` VALUES (1,14,2,'Member','2026-03-03'),(2,18,3,'Member','2026-03-03');
/*!40000 ALTER TABLE `committeemembership` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty` (
  `userId` int NOT NULL,
  `designation` varchar(50) DEFAULT NULL,
  `department` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`userId`),
  CONSTRAINT `faculty_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`userId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty`
--

LOCK TABLES `faculty` WRITE;
/*!40000 ALTER TABLE `faculty` DISABLE KEYS */;
INSERT INTO `faculty` VALUES (32,NULL,'CSE'),(34,NULL,'CSE');
/*!40000 ALTER TABLE `faculty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `higherstudies`
--

DROP TABLE IF EXISTS `higherstudies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `higherstudies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `university` varchar(150) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `courseName` varchar(150) DEFAULT NULL,
  `applicationDate` date DEFAULT NULL,
  `admissionStatus` varchar(50) DEFAULT NULL,
  `proof_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `userId` (`userId`),
  CONSTRAINT `higherstudies_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`userId`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `higherstudies`
--

LOCK TABLES `higherstudies` WRITE;
/*!40000 ALTER TABLE `higherstudies` DISABLE KEYS */;
INSERT INTO `higherstudies` VALUES (1,12,'nirma','usa','computer','2026-03-03','applied',NULL),(2,18,'nirma','usa','computer','2026-03-03','applied',NULL),(3,18,'nirma','usa','computer','2026-03-03','applied','user18_20260305_100608_implementaion_project_1.pdf'),(4,14,'nirma','usa','computer','2026-03-03','applied','user14_20260307_152358_1-s2.0-S0952197624021067-main.pdf'),(5,14,'nirma','usa','computer','2026-03-03','applied','user14_20260309_103657_Daily_worksheetDWS.pdf'),(6,14,'nirma','usa','computer','2026-03-03','applied','user14_20260309_103918_EMotivEpoc.pdf');
/*!40000 ALTER TABLE `higherstudies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message`
--

DROP TABLE IF EXISTS `message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `message` (
  `messageId` int NOT NULL AUTO_INCREMENT,
  `senderId` int NOT NULL,
  `receiverId` int NOT NULL,
  `content` text NOT NULL,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`messageId`),
  KEY `senderId` (`senderId`),
  KEY `receiverId` (`receiverId`),
  CONSTRAINT `message_ibfk_1` FOREIGN KEY (`senderId`) REFERENCES `user` (`userId`),
  CONSTRAINT `message_ibfk_2` FOREIGN KEY (`receiverId`) REFERENCES `user` (`userId`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message`
--

LOCK TABLES `message` WRITE;
/*!40000 ALTER TABLE `message` DISABLE KEYS */;
INSERT INTO `message` VALUES (1,16,18,'hello','2026-03-18 04:06:33'),(2,16,14,'hello','2026-03-18 04:13:32'),(3,16,18,'aGVsbG8=','2026-03-18 04:56:57'),(4,34,14,'aGVsbG8=','2026-03-19 04:46:31');
/*!40000 ALTER TABLE `message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `placement`
--

DROP TABLE IF EXISTS `placement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `placement` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `companyName` varchar(100) DEFAULT NULL,
  `jobRole` varchar(100) DEFAULT NULL,
  `package` varchar(50) DEFAULT NULL,
  `status` varchar(30) DEFAULT NULL,
  `placementYear` int DEFAULT NULL,
  `proof_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `userId` (`userId`),
  CONSTRAINT `placement_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`userId`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `placement`
--

LOCK TABLES `placement` WRITE;
/*!40000 ALTER TABLE `placement` DISABLE KEYS */;
INSERT INTO `placement` VALUES (1,11,'Infosys','Backend Developer','7 LPA','Placed',2026,NULL,'2026-02-18 05:59:50'),(9,14,'microsoft','software engineer','17','Selected',2025,NULL,'2026-03-03 03:40:13'),(10,14,'microsoft','software engineer','17','Selected',2025,NULL,'2026-03-03 03:44:31'),(11,18,'google','software engineer','17','Selected',2025,NULL,'2026-03-03 06:09:34'),(12,18,'google','software engineer','17','Selected',2025,'offer_u18_20260305_101426_4EC505_DA_Course_Design_Policy.pdf','2026-03-05 04:44:26'),(13,18,'google','software engineer','17','Selected',2025,'offer_u18_20260318_105950_22BCE024._AshishKumar_bhedi.pdf','2026-03-18 05:29:50');
/*!40000 ALTER TABLE `placement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `userId` int NOT NULL,
  `rollNumber` varchar(20) NOT NULL,
  `program` varchar(50) DEFAULT NULL,
  `semester` int DEFAULT NULL,
  `department` varchar(50) DEFAULT NULL,
  `sgpa` float DEFAULT '0',
  `cgpa` float DEFAULT '0',
  `attendance_percentage` float DEFAULT '0',
  `isPlanningHigherStudies` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`userId`),
  UNIQUE KEY `rollNumber` (`rollNumber`),
  CONSTRAINT `student_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`userId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES (11,'22CS001','BTech',6,'CSE',0,0,0,0),(12,'CS101','BTech',6,'CSE',0,0,0,1),(14,'22BCE024','B.Tech',8,'CSE',8.2,8,85.5,1),(15,'ADMIN',NULL,NULL,NULL,0,0,0,0),(16,'DRABC',NULL,NULL,NULL,0,0,0,0),(17,'22BCE025',NULL,NULL,NULL,0,0,0,1),(18,'22BCE026','B.Tech',4,'CSE',0,0,0,1),(22,'22BCE030',NULL,NULL,NULL,0,0,0,0),(24,'22BCE242',NULL,NULL,NULL,0,0,0,0);
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `studentactivity`
--

DROP TABLE IF EXISTS `studentactivity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `studentactivity` (
  `studentActivityId` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `activityId` int NOT NULL,
  PRIMARY KEY (`studentActivityId`),
  UNIQUE KEY `userId` (`userId`,`activityId`),
  KEY `activityId` (`activityId`),
  CONSTRAINT `studentactivity_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `student` (`userId`),
  CONSTRAINT `studentactivity_ibfk_2` FOREIGN KEY (`activityId`) REFERENCES `activity` (`activityId`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `studentactivity`
--

LOCK TABLES `studentactivity` WRITE;
/*!40000 ALTER TABLE `studentactivity` DISABLE KEYS */;
INSERT INTO `studentactivity` VALUES (6,14,10),(7,18,11),(8,18,12);
/*!40000 ALTER TABLE `studentactivity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `testimonials`
--

DROP TABLE IF EXISTS `testimonials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `testimonials` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `content` text NOT NULL,
  `date_added` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_featured` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `userId` (`userId`),
  CONSTRAINT `testimonials_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`userId`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `testimonials`
--

LOCK TABLES `testimonials` WRITE;
/*!40000 ALTER TABLE `testimonials` DISABLE KEYS */;
/*!40000 ALTER TABLE `testimonials` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `userId` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('student','faculty','admin') NOT NULL,
  `phoneNumber` varchar(15) DEFAULT NULL,
  `address` text,
  `lastLogin` datetime DEFAULT NULL,
  `otp_code` varchar(6) DEFAULT NULL,
  `otp_expiry` datetime DEFAULT NULL,
  `permissions` varchar(255) DEFAULT '',
  `profile_image` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`userId`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (2,'Student','test2@example.com','scrypt:32768:8:1$lxpvQhgijiH3QKRH$7bbc4c40780c712285c3c7d33330ab6dccc43e9420b3e397e2a312b43be2ed645b098b8167952cd6452fcce318d33fda1a3792ac7e5f4013204147f8a4022fd7','student',NULL,NULL,NULL,NULL,NULL,'',NULL),(4,'Student','test5@example.com','scrypt:32768:8:1$WModLBDzpOn6zaeD$245340ff838e3c0865e3c515670504b5e0d6361e81bbc37fe2b10346fe4e6f27072b1b5dd836a6c5448f85e8646da97b2be0989a744f396576381b461d07e281','student',NULL,NULL,NULL,NULL,NULL,'',NULL),(5,'John','john@gmail.com','scrypt:32768:8:1$JynTAugnX3ImQbXm$e0061e057ae70c73c0304d125bd83df0fae3eb646cd372a086187ec922628bbc5cae208d13049523e9c0234ab9f830f5d349bd77b58082250c78a7fa9d83f548','student',NULL,NULL,NULL,NULL,NULL,'',NULL),(6,'Admin','admin@gmail.com','scrypt:32768:8:1$YA9jBZ7VpLCCKgsM$9eef9bc6f104c1764f1f3f3451ec2527854ae5713ff250f2161a91028e0a2463e7c1d1e5faafcb0335eeab0b05ac76578bed886efc6c3b1873e65bba0f453a51','admin',NULL,NULL,NULL,NULL,NULL,'',NULL),(8,'Test Student','student1@gmail.com','scrypt:32768:8:1$0bAS50rSwVPxAuDC$43fa714dafe335c2c400a3528d465cb8338468379963ca0eed0844b7ed1b6d02b792cbf8ca2c5554ae3ecf7a4f794dc5034e6eb032e8bf4d2e62571997f54d2f','student',NULL,NULL,NULL,NULL,NULL,'',NULL),(9,'Test Student','student2@gmail.com','scrypt:32768:8:1$C1SCxhOo2bGPUHJ1$946f5d05113cfdcfc4272431c71a18e38cbaaf031b723c9ee1b45860cbda6456d7b1c81d72399f12f1aeb0c5d783d795e24952185a42d48a259bd937da59933e','student',NULL,NULL,NULL,NULL,NULL,'',NULL),(10,'Test Student','student3@gmail.com','scrypt:32768:8:1$yLnJreq2FE2gPQi1$d07f66fc8958f76bd6c1bdfddef3bebbdcb139093cb2bd3c602e064e85fe3dc4df896050512afc98737b7b39c30538c64e452b647293b56af5d881c51811b305','student',NULL,NULL,NULL,NULL,NULL,'',NULL),(11,'Test Student','student4@gmail.com','scrypt:32768:8:1$sNXbIiRNO4EB2qK7$977e07d2718a3959d5903e8c9f728541f738ff4763a160362422e2680ed1fc754e55fa8c88211e66ca990b9e610068f134ae06b504e7a86517631dba289f2fbc','student',NULL,NULL,NULL,NULL,NULL,'',NULL),(12,'John Doe','test@test.com','scrypt:32768:8:1$w3hXr5JyJe9Kqvwi$d9383582cecd208fd97d197966ae97c5206bc24ce9c7456eeb5ddc62e8913b8361a3bf6f73669a8a4fd272bc29bb0dba657f697aedd0c8020d6ca12cefc631d4','student','9876543210','Chennai',NULL,NULL,NULL,'',NULL),(13,'Pending','student@gmail.com','scrypt:32768:8:1$jqYCFq0Q7R07HP6r$428188a37ca3a1e0bd498f974c7ae59d64d1ec43413165be7438ef96359e52d64ef8adb660dbb3f808e4b0c9346b13c0a2205377f5f0a5c3a1207a7b17b59c1f','student',NULL,NULL,NULL,NULL,NULL,'',NULL),(14,'Ashish','22bce024@nirmauni.ac.in','scrypt:32768:8:1$pxII595LH5wnLq0d$e2b5b0ee187a61dbe29b08b33280fb35a35b0277283e4d82a0f75c4945a72f842de8a2980e023f3cf5ba42e502ab165a6164ed175b649bfada2f73fa7d6d0ca7','student','9081701379','gfkbdasdk',NULL,'705690','2026-03-06 13:21:58','','user_14.jpg'),(15,'System Admin','admin@portal.com','scrypt:32768:8:1$HMR3JIn302RTamNJ$9f74aa070ba278846caf5d83352b37a27296c646ae7ea0989e8103fcfdea93e922ca0da7a10dd62486aaed967364d77b16c8e12e822bed7f5e69af1df60b410c','admin',NULL,NULL,NULL,NULL,NULL,'',NULL),(16,'Dr. ABC','drabc@faculty.com','scrypt:32768:8:1$ojXEWudh6HF8jCKc$7da4b50b015ba197b199a9fe84dd1d119bcfed92b77299b3d1a4140a21c3a7a526382962d0e8a9adcf31d1ed56df56fbde297606a97bed6b995243357a1437ce','faculty',NULL,NULL,NULL,NULL,NULL,'view_activities,view_placement,post_announcement',NULL),(17,'New Student','22bce025@nirmauni.ac.in','scrypt:32768:8:1$cQ2uXKfKNp8wLLdq$7828f20b5b263c1180d0530bf08767871db0adc6ce02ce0ba267a31d4ee97a612f432629cd52073c576a33b46a2b49599e2abb39c2387f3a7eeeb28c53e1a37f','student',NULL,NULL,NULL,NULL,NULL,'',NULL),(18,'test','22bce026@nirmauni.ac.in','scrypt:32768:8:1$KU95c9NodNSXbgbf$ec1b5915babbbe55a98bfeed1899866ef3fc3b270855bef1eb35b3d3b7ad1d31f267e216b88b1062fc020ce6fa8fbb1ac4be8e334f9ea1a8d054b752571bee44','student','+919081701379','hh',NULL,NULL,NULL,'','user_18.jpg'),(22,'New Student','22bce030@nirmauni.ac.in','scrypt:32768:8:1$Af4huFpYjaLPhqbz$d4196ffd7670a99ff35ca750ae10f769f9c8852ff028f5c9ee65c9eeb2835cdb311f23d6273001cc8cba807204143c35dfd3b110b9fe1f5a9d0adb0a23388e28','student',NULL,NULL,NULL,NULL,NULL,'',NULL),(24,'New Student','22bce242@nirmauni.ac.in','scrypt:32768:8:1$fJdrUptihWc9VN3k$d489f26c081627c727b2630e8f9275b6204a4573ac3acd6680d0abb3c7f39151e1d2ceba4b82a468dd3102eb585f9e9c434a86208fc67af2f48f16c13eaa5817','student',NULL,NULL,NULL,NULL,NULL,'',NULL),(32,'Nobody','ashishbhedi75@gmail.com','scrypt:32768:8:1$LoJUGAdr9zDjDoWo$37507add8736773507ef8319d3e42d04ad3312e7a492e3e2cd45efcfc4d4f350a968029ea43a634a8bcd0e2328fcdf4493e68d83777e85a228ff33eed07d656c','faculty',NULL,NULL,NULL,NULL,NULL,'',NULL),(34,'Sharada Valiveti','sharada.valiveti@nirmauni.ac.in','scrypt:32768:8:1$CST5N5ObRyx3ANTY$c7b945a5520b0c19d86d0c21e227df70dff52874c4ad5b4abf63c750c951872d86b847a4cdab3f250ba999a69df7ec9e1246c41661771b2424adb8de4a35876f','faculty',NULL,NULL,NULL,NULL,NULL,'',NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-23 12:59:51
