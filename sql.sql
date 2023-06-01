CREATE DATABASE test;
USE test;
create table data_set_owner (owner_kpp VARCHAR(100) PRIMARY KEY,region VARCHAR(100),owner_adress VARCHAR(200),owner_tel VARCHAR(11),owner_email VARCHAR(50));
create table data_set_passport (id_passport INT PRIMARY KEY AUTO_INCREMENT,data_set_name VARCHAR(200),data_set_description TEXT(500),publication_date DATETIME,update_date DATETIME,update_description TEXT(500),id_category INT,owner_kpp VARCHAR(9));
create table data_set (id_data_set INT PRIMARY KEY AUTO_INCREMENT,file_path VARCHAR(100),id_passport INT);

