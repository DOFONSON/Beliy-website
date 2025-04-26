-- Создаем пользователя, если он не существует
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'bely_user') THEN
      CREATE USER bely_user WITH PASSWORD 'bely_pass';
   END IF;
END
$do$;

-- Удаляем базу данных, если она существует
DROP DATABASE IF EXISTS bely_db;

-- Создаем базу данных
CREATE DATABASE bely_db
    WITH 
    OWNER = bely_user
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TEMPLATE template0; 