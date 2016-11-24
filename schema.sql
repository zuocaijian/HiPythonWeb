DROP DATABASE IF EXISTS awesome;

CREATE DATABASE awesome;

USE awesome;

GRANT SELECT, INSERT, UPDATE, DELETE ON awesome.* TO 'www-data'@'localhost'
IDENTIFIED BY 'www-data';

CREATE TABLE users (
  `id`        VARCHAR(50)  NOT NULL,
  `email`     VARCHAR(50)  NOT NULL,
  `passwd`    VARCHAR(50)  NOT NULL,
  `admin`     VARCHAR(50)  NOT NULL,
  `name`      VARCHAR(50)  NOT NULL,
  `image`     VARCHAR(500) NOT NULL,
  `create_at` REAL         NOT NULL,
  UNIQUE KEY `idx_email` (`email`),
  KEY `idx_created_at` (`create_at`),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;


CREATE TABLE blogs (
  `id`         VARCHAR(50)  NOT NULL,
  `user_id`    VARCHAR(50)  NOT NULL,
  `user_name`  VARCHAR(50)  NOT NULL,
  `user_image` VARCHAR(500) NOT NULL,
  `name`       VARCHAR(50)  NOT NULL,
  `summary`    VARCHAR(200) NOT NULL,
  `content`    MEDIUMTEXT   NOT NULL,
  `create_at`  REAL         NOT NULL,
  KEY `idx_create_at` (`create_at`),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;


CREATE TABLE comments (
  `id`         VARCHAR(50)  NOT NULL,
  `blog_id`    VARCHAR(50)  NOT NULL,
  `user_id`    VARCHAR(50)  NOT NULL,
  `user_name`  VARCHAR(50)  NOT NULL,
  `user_image` VARCHAR(500) NOT NULL,
  `content`    MEDIUMTEXT   NOT NULL,
  `create_at`  REAL         NOT NULL,
  KEY `idx_create_at` (`create_at`),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;