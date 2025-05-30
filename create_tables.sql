-- Create food_entry table
CREATE TABLE IF NOT EXISTS `food_entry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `name` varchar(120) NOT NULL,
  `calories` float DEFAULT NULL,
  `protein` float DEFAULT NULL,
  `carbs` float DEFAULT NULL,
  `fat` float DEFAULT NULL,
  `date` datetime NOT NULL DEFAULT current_timestamp(),
  `description` text DEFAULT NULL,
  `image_filename` varchar(255) DEFAULT NULL,
  `image_analysis` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `food_entry_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci; 