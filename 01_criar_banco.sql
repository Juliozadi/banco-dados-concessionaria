-- =============================================================
-- BANCO DE DADOS DE UMA CONCESSIONÁRIA DE VEÍCULOS
-- SGBD: PostgreSQL 16
--
-- ARQUIVO 1 DE 2: CRIAÇÃO DO BANCO DE DADOS
-- Execute conectado ao banco padrão "postgres":
--   Terminal: psql -U postgres -f 01_criar_banco.sql
--   pgAdmin:  Query Tool no banco postgres; selecione UM comando
--             por vez e tecle F5 (o PostgreSQL não aceita DROP e
--             CREATE DATABASE enviados juntos no mesmo bloco)
-- =============================================================

-- Apaga uma versão anterior para que o script possa ser executado
-- novamente sem erro
DROP DATABASE IF EXISTS concessionaria_db;

CREATE DATABASE concessionaria_db
    WITH ENCODING = 'UTF8'
         TEMPLATE = template0;
