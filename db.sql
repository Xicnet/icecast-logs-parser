CREATE TABLE `icecast_logs` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`datetime_start` DATETIME NOT NULL,
	`datetime_end` DATETIME NULL DEFAULT NULL,
	`ip` VARCHAR(20) NOT NULL,
	`country_code` VARCHAR(4) NULL DEFAULT NULL,
	`mount` VARCHAR(90) NOT NULL,
	`status_code` INT(11) NULL DEFAULT NULL,
	`duration` INT(11) NULL DEFAULT NULL,
	`sent_bytes` INT(11) NULL DEFAULT NULL,
	`agent` VARCHAR(200) NULL DEFAULT NULL,
	`referer` VARCHAR(400) NULL DEFAULT NULL,
	`server` VARCHAR(50) NULL DEFAULT NULL,
	`auth_user` VARCHAR(20) NULL DEFAULT NULL,
	`auth_pass` VARCHAR(20) NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
) COLLATE='utf8_general_ci' ENGINE=MyISAM
