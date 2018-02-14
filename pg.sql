CREATE TABLE icecast_logs (
	id SERIAL,
	datetime_start timestamp,
	datetime_end timestamp,
	ip varchar(20) NOT NULL,
	country_code varchar(4) NULL DEFAULT NULL,
	mount varchar(90) NOT NULL,
	status_code integer NULL DEFAULT NULL,
	duration integer NULL DEFAULT NULL,
	sent_bytes integer NULL DEFAULT NULL,
	agent varchar(200) NULL DEFAULT NULL,
	referer varchar(400) NULL DEFAULT NULL,
	server varchar(50) NULL DEFAULT NULL,
	auth_user varchar(20) NULL DEFAULT NULL,
	auth_pass varchar(20) NULL DEFAULT NULL
);
