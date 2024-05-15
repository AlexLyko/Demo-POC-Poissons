--
-- PostgreSQL database dump
--

-- Dumped from database version 13.11 (Debian 13.11-1.pgdg100+1)
-- Dumped by pg_dump version 14.3

-- Started on 2023-09-11 13:52:23

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 6 (class 2615 OID 14348283)
-- Name: poc; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA poc;


ALTER SCHEMA poc OWNER TO postgres;

--
-- TOC entry 202 (class 1259 OID 14348290)
-- Name: questions_id_series_seq; Type: SEQUENCE; Schema: poc; Owner: postgres
--

CREATE SEQUENCE poc.questions_id_series_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE poc.questions_id_series_seq OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 203 (class 1259 OID 14348292)
-- Name: questions; Type: TABLE; Schema: poc; Owner: postgres
--

CREATE TABLE poc.questions (
    id_series bigint DEFAULT nextval('poc.questions_id_series_seq'::regclass) NOT NULL,
    score text,
    mat_id character varying(64) NOT NULL,
    estimated_difficulty bigint,
    level character varying(32),
    profile character varying(32),
    content json,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE poc.questions OWNER TO postgres;

--
-- TOC entry 201 (class 1259 OID 14348284)
-- Name: users; Type: TABLE; Schema: poc; Owner: postgres
--

CREATE TABLE poc.users (
    mat_id character varying(64) NOT NULL,
    current_score bigint DEFAULT 0 NOT NULL,
    pass character varying(64) DEFAULT md5('3H1ZRhlsQA4vMbmI0yDO'::text) NOT NULL
);


ALTER TABLE poc.users OWNER TO postgres;


--
-- TOC entry 2961 (class 0 OID 0)
-- Dependencies: 202
-- Name: questions_id_series_seq; Type: SEQUENCE SET; Schema: poc; Owner: postgres
--

SELECT pg_catalog.setval('poc.questions_id_series_seq', 36, true);


--
-- TOC entry 2817 (class 2606 OID 14348300)
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: poc; Owner: postgres
--

ALTER TABLE ONLY poc.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (id_series);


--
-- TOC entry 2815 (class 2606 OID 14348289)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: poc; Owner: postgres
--

ALTER TABLE ONLY poc.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (mat_id);


--
-- TOC entry 2818 (class 2606 OID 14348301)
-- Name: questions mat_id; Type: FK CONSTRAINT; Schema: poc; Owner: postgres
--

ALTER TABLE ONLY poc.questions
    ADD CONSTRAINT mat_id FOREIGN KEY (mat_id) REFERENCES poc.users(mat_id) NOT VALID;


--
-- TOC entry 2957 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA poc; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA poc TO pocpoisson;


--
-- TOC entry 2958 (class 0 OID 0)
-- Dependencies: 202
-- Name: SEQUENCE questions_id_series_seq; Type: ACL; Schema: poc; Owner: postgres
--

GRANT ALL ON SEQUENCE poc.questions_id_series_seq TO pocpoisson;


--
-- TOC entry 2959 (class 0 OID 0)
-- Dependencies: 203
-- Name: TABLE questions; Type: ACL; Schema: poc; Owner: postgres
--

GRANT ALL ON TABLE poc.questions TO pocpoisson;


--
-- TOC entry 2960 (class 0 OID 0)
-- Dependencies: 201
-- Name: TABLE users; Type: ACL; Schema: poc; Owner: postgres
--

GRANT ALL ON TABLE poc.users TO pocpoisson;


--
-- TOC entry 1717 (class 826 OID 14348307)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: poc; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA poc GRANT ALL ON TABLES  TO pocpoisson;


-- Completed on 2023-09-11 13:52:25

--
-- PostgreSQL database dump complete
--

