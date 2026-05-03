-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: db_epson_k3
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `camera`
--

DROP TABLE IF EXISTS `camera`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `camera` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `area_name` varchar(150) NOT NULL COMMENT 'Nama area/lokasi kamera',
  `status_cam` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Status aktif kamera',
  PRIMARY KEY (`id`),
  KEY `ix_camera_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `camera`
--

LOCK TABLES `camera` WRITE;
/*!40000 ALTER TABLE `camera` DISABLE KEYS */;
INSERT INTO `camera` VALUES (1,'Area Produksi A',1),(2,'Area Gudang B',1);
/*!40000 ALTER TABLE `camera` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` text NOT NULL COMMENT 'bcrypt hashed password',
  `role` enum('admin','manager') NOT NULL DEFAULT 'manager',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_user_username` (`username`),
  KEY `ix_user_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin_k3','$2b$12$4vQJtBtYh8dGAMY80GSNT.I6NJLm9jFqTscLk675LZl/uR.mv7ekm','admin'),(2,'manager_area_b','$2b$12$Qj7D9VzOAOEh5O8d3zZUOO0YpxYgpjPc4iPLg24b4x1nr6fdqmM92','manager'),(3,'manager_area_a','$2b$12$Tw/wxG3f1iiOJFVHzYZCY..V63MHdELT1gsV8vRmW0wLvKKP5Z0SW','manager');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `violation_log`
--

DROP TABLE IF EXISTS `violation_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `violation_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `camera_id` int(11) DEFAULT NULL COMMENT 'ID kamera sumber deteksi',
  `violation_type_id` int(11) DEFAULT NULL COMMENT 'ID jenis pelanggaran',
  `image_path` varchar(500) DEFAULT NULL COMMENT 'Path/URL foto bukti pelanggaran',
  `created_at` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Waktu deteksi pelanggaran',
  `status` enum('Belum Ditindak','Sudah Ditindak') NOT NULL DEFAULT 'Belum Ditindak',
  PRIMARY KEY (`id`),
  KEY `ix_violation_log_violation_type_id` (`violation_type_id`),
  KEY `ix_violation_log_camera_id` (`camera_id`),
  KEY `ix_violation_log_id` (`id`),
  KEY `ix_violation_log_created_at` (`created_at`),
  CONSTRAINT `violation_log_ibfk_1` FOREIGN KEY (`camera_id`) REFERENCES `camera` (`id`) ON DELETE SET NULL,
  CONSTRAINT `violation_log_ibfk_2` FOREIGN KEY (`violation_type_id`) REFERENCES `violation_type` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `violation_log`
--

LOCK TABLES `violation_log` WRITE;
/*!40000 ALTER TABLE `violation_log` DISABLE KEYS */;
INSERT INTO `violation_log` VALUES (1,1,1,'uploads\\7690487e1a974b4d8583034d0f0fd524.jpeg','2026-04-25 06:33:44','Sudah Ditindak'),(2,1,3,'uploads\\423a4c66f42942809b87ce6a79d28563.jpg','2026-04-25 06:34:59','Belum Ditindak'),(3,2,2,'uploads\\f91e140045834ab881cedbf3e8625305.jpg','2026-04-25 06:35:21','Belum Ditindak');
/*!40000 ALTER TABLE `violation_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `violation_type`
--

DROP TABLE IF EXISTS `violation_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `violation_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `yolo_class_id` int(11) NOT NULL COMMENT 'Index class dari YOLO (0, 1, 2)',
  `label_name` varchar(100) NOT NULL COMMENT 'Label YOLO untuk jenis pelanggaran (misal: Tidak Pakai Helm)',
  `penalty_score` int(11) NOT NULL COMMENT 'Skor penalti untuk pelanggaran ini',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_violation_type_label_name` (`label_name`),
  UNIQUE KEY `ix_violation_type_yolo_class_id` (`yolo_class_id`),
  KEY `ix_violation_type_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `violation_type`
--

LOCK TABLES `violation_type` WRITE;
/*!40000 ALTER TABLE `violation_type` DISABLE KEYS */;
INSERT INTO `violation_type` VALUES (1,0,'Tidak Pakai Helm',3),(2,1,'Tidak Pakai Rompi',2),(3,2,'Tidak Pakai Sarung Tangan',1);
/*!40000 ALTER TABLE `violation_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'db_epson_k3'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-28 15:34:44
