--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.0
-- Dumped by pg_dump version 9.1.2
-- Started on 2012-01-22 18:14:50 MSK

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 1982 (class 1262 OID 16393)
-- Name: fido; Type: DATABASE; Schema: -; Owner: fido
--

CREATE DATABASE fido WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'ru_RU.UTF-8' LC_CTYPE = 'ru_RU.UTF-8';


ALTER DATABASE fido OWNER TO fido;

\connect fido

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 183 (class 3079 OID 11638)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 1985 (class 0 OID 0)
-- Dependencies: 183
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- TOC entry 195 (class 1255 OID 230635)
-- Dependencies: 5
-- Name: n_5(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION n_5() RETURNS integer
    LANGUAGE sql IMMUTABLE STRICT
    AS $$
SELECT 5;
$$;


ALTER FUNCTION public.n_5() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 162 (class 1259 OID 16396)
-- Dependencies: 5
-- Name: addresses; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE addresses (
    id bigint NOT NULL,
    domain integer,
    text character varying,
    owner character varying,
    "group" bigint
);


ALTER TABLE public.addresses OWNER TO postgres;

--
-- TOC entry 161 (class 1259 OID 16394)
-- Dependencies: 162 5
-- Name: addresses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE addresses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.addresses_id_seq OWNER TO postgres;

--
-- TOC entry 1987 (class 0 OID 0)
-- Dependencies: 161
-- Name: addresses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE addresses_id_seq OWNED BY addresses.id;


--
-- TOC entry 178 (class 1259 OID 347388)
-- Dependencies: 5
-- Name: deletedvitalsubscriptionwatermarks; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE deletedvitalsubscriptionwatermarks (
    id bigint NOT NULL,
    target bigint,
    subscriber bigint,
    message bigint
);


ALTER TABLE public.deletedvitalsubscriptionwatermarks OWNER TO postgres;

--
-- TOC entry 177 (class 1259 OID 347386)
-- Dependencies: 5 178
-- Name: deletedvitalsubscriptionwatermarks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE deletedvitalsubscriptionwatermarks_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.deletedvitalsubscriptionwatermarks_id_seq OWNER TO postgres;

--
-- TOC entry 1989 (class 0 OID 0)
-- Dependencies: 177
-- Name: deletedvitalsubscriptionwatermarks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE deletedvitalsubscriptionwatermarks_id_seq OWNED BY deletedvitalsubscriptionwatermarks.id;


--
-- TOC entry 164 (class 1259 OID 16409)
-- Dependencies: 5
-- Name: domains; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE domains (
    id integer NOT NULL,
    name character varying NOT NULL,
    verifysubscriptions boolean
);


ALTER TABLE public.domains OWNER TO postgres;

--
-- TOC entry 163 (class 1259 OID 16407)
-- Dependencies: 164 5
-- Name: domains_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE domains_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.domains_id_seq OWNER TO postgres;

--
-- TOC entry 1991 (class 0 OID 0)
-- Dependencies: 163
-- Name: domains_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE domains_id_seq OWNED BY domains.id;


--
-- TOC entry 182 (class 1259 OID 798322)
-- Dependencies: 5
-- Name: lastsent; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE lastsent (
    id bigint NOT NULL,
    subscriber bigint,
    domain bigint,
    lastsent bigint
);


ALTER TABLE public.lastsent OWNER TO postgres;

--
-- TOC entry 181 (class 1259 OID 798320)
-- Dependencies: 5 182
-- Name: lastsent_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE lastsent_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lastsent_id_seq OWNER TO postgres;

--
-- TOC entry 1992 (class 0 OID 0)
-- Dependencies: 181
-- Name: lastsent_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE lastsent_id_seq OWNED BY lastsent.id;


--
-- TOC entry 170 (class 1259 OID 16466)
-- Dependencies: 1926 1927 1928 5
-- Name: links; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE links (
    id bigint NOT NULL,
    address bigint,
    authentication xml,
    connection xml,
    pktn bigint DEFAULT 0 NOT NULL,
    bundlen bigint DEFAULT 0 NOT NULL,
    ticn bigint DEFAULT 0 NOT NULL
);


ALTER TABLE public.links OWNER TO postgres;

--
-- TOC entry 169 (class 1259 OID 16464)
-- Dependencies: 170 5
-- Name: links_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE links_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.links_id_seq OWNER TO postgres;

--
-- TOC entry 1994 (class 0 OID 0)
-- Dependencies: 169
-- Name: links_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE links_id_seq OWNED BY links.id;


--
-- TOC entry 180 (class 1259 OID 663138)
-- Dependencies: 1918 5
-- Name: links_simple; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW links_simple AS
    SELECT l.domain AS link_domain, l.text AS link_address, links.authentication, links.connection FROM links, addresses l WHERE (l.id = links.address);


ALTER TABLE public.links_simple OWNER TO postgres;

--
-- TOC entry 174 (class 1259 OID 122735)
-- Dependencies: 5
-- Name: listings; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE listings (
    id bigint NOT NULL,
    address bigint,
    list bigint
);


ALTER TABLE public.listings OWNER TO postgres;

--
-- TOC entry 173 (class 1259 OID 122732)
-- Dependencies: 174 5
-- Name: listings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE listings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.listings_id_seq OWNER TO postgres;

--
-- TOC entry 1996 (class 0 OID 0)
-- Dependencies: 173
-- Name: listings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE listings_id_seq OWNED BY listings.id;


--
-- TOC entry 172 (class 1259 OID 114056)
-- Dependencies: 5
-- Name: lists; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE lists (
    id bigint NOT NULL,
    name character varying
);


ALTER TABLE public.lists OWNER TO postgres;

--
-- TOC entry 171 (class 1259 OID 114054)
-- Dependencies: 172 5
-- Name: lists_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE lists_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lists_id_seq OWNER TO postgres;

--
-- TOC entry 1997 (class 0 OID 0)
-- Dependencies: 171
-- Name: lists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE lists_id_seq OWNED BY lists.id;


--
-- TOC entry 166 (class 1259 OID 16422)
-- Dependencies: 1922 5
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE messages (
    id bigint NOT NULL,
    source bigint,
    destination bigint,
    header xml,
    body text,
    processed integer DEFAULT 0 NOT NULL,
    msgid character varying NOT NULL,
    receivedfrom bigint
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- TOC entry 165 (class 1259 OID 16420)
-- Dependencies: 166 5
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE messages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO postgres;

--
-- TOC entry 1999 (class 0 OID 0)
-- Dependencies: 165
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE messages_id_seq OWNED BY messages.id;


--
-- TOC entry 179 (class 1259 OID 663034)
-- Dependencies: 1917 5
-- Name: messages_simple; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW messages_simple AS
    SELECT f.domain AS from_domain, f.text AS from_address, t.domain AS to_domain, t.text AS to_address, m.header, m.body, m.processed, m.msgid, m.receivedfrom FROM messages m, addresses f, addresses t WHERE ((t.id = m.destination) AND (f.id = m.source)) ORDER BY m.id;


ALTER TABLE public.messages_simple OWNER TO postgres;

--
-- TOC entry 176 (class 1259 OID 129556)
-- Dependencies: 5
-- Name: process_status; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE process_status (
    id integer NOT NULL,
    name character varying
);


ALTER TABLE public.process_status OWNER TO postgres;

--
-- TOC entry 175 (class 1259 OID 129554)
-- Dependencies: 176 5
-- Name: process_status_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE process_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.process_status_id_seq OWNER TO postgres;

--
-- TOC entry 2001 (class 0 OID 0)
-- Dependencies: 175
-- Name: process_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE process_status_id_seq OWNED BY process_status.id;


--
-- TOC entry 168 (class 1259 OID 16448)
-- Dependencies: 1924 5
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE subscriptions (
    id bigint NOT NULL,
    vital boolean,
    target bigint,
    subscriber bigint,
    lastsent bigint DEFAULT (-1) NOT NULL,
    commuter integer
);


ALTER TABLE public.subscriptions OWNER TO postgres;

--
-- TOC entry 2002 (class 0 OID 0)
-- Dependencies: 168
-- Name: COLUMN subscriptions.vital; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN subscriptions.vital IS 'tossing message without vital subscription (uplink for echo, nexthop for netmail) must fail ';


--
-- TOC entry 167 (class 1259 OID 16446)
-- Dependencies: 5 168
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE subscriptions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subscriptions_id_seq OWNER TO postgres;

--
-- TOC entry 2004 (class 0 OID 0)
-- Dependencies: 167
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE subscriptions_id_seq OWNED BY subscriptions.id;


--
-- TOC entry 1919 (class 2604 OID 16399)
-- Dependencies: 161 162 162
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE addresses ALTER COLUMN id SET DEFAULT nextval('addresses_id_seq'::regclass);


--
-- TOC entry 1932 (class 2604 OID 347391)
-- Dependencies: 177 178 178
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE deletedvitalsubscriptionwatermarks ALTER COLUMN id SET DEFAULT nextval('deletedvitalsubscriptionwatermarks_id_seq'::regclass);


--
-- TOC entry 1920 (class 2604 OID 16412)
-- Dependencies: 163 164 164
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE domains ALTER COLUMN id SET DEFAULT nextval('domains_id_seq'::regclass);


--
-- TOC entry 1933 (class 2604 OID 798325)
-- Dependencies: 182 181 182
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE lastsent ALTER COLUMN id SET DEFAULT nextval('lastsent_id_seq'::regclass);


--
-- TOC entry 1925 (class 2604 OID 16469)
-- Dependencies: 170 169 170
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE links ALTER COLUMN id SET DEFAULT nextval('links_id_seq'::regclass);


--
-- TOC entry 1930 (class 2604 OID 122738)
-- Dependencies: 173 174 174
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE listings ALTER COLUMN id SET DEFAULT nextval('listings_id_seq'::regclass);


--
-- TOC entry 1929 (class 2604 OID 114059)
-- Dependencies: 172 171 172
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE lists ALTER COLUMN id SET DEFAULT nextval('lists_id_seq'::regclass);


--
-- TOC entry 1921 (class 2604 OID 16425)
-- Dependencies: 165 166 166
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE messages ALTER COLUMN id SET DEFAULT nextval('messages_id_seq'::regclass);


--
-- TOC entry 1931 (class 2604 OID 129559)
-- Dependencies: 176 175 176
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE process_status ALTER COLUMN id SET DEFAULT nextval('process_status_id_seq'::regclass);


--
-- TOC entry 1923 (class 2604 OID 16451)
-- Dependencies: 167 168 168
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE subscriptions ALTER COLUMN id SET DEFAULT nextval('subscriptions_id_seq'::regclass);


--
-- TOC entry 1935 (class 2606 OID 16406)
-- Dependencies: 162 162 162
-- Name: addresses_domain_text_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY addresses
    ADD CONSTRAINT addresses_domain_text_key UNIQUE (domain, text);


--
-- TOC entry 1937 (class 2606 OID 16404)
-- Dependencies: 162 162
-- Name: addresses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (id);


--
-- TOC entry 1939 (class 2606 OID 16419)
-- Dependencies: 164 164
-- Name: domains_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY domains
    ADD CONSTRAINT domains_name_key UNIQUE (name);


--
-- TOC entry 1941 (class 2606 OID 16417)
-- Dependencies: 164 164
-- Name: domains_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY domains
    ADD CONSTRAINT domains_pkey PRIMARY KEY (id);


--
-- TOC entry 1964 (class 2606 OID 798327)
-- Dependencies: 182 182
-- Name: lastsent_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY lastsent
    ADD CONSTRAINT lastsent_pkey PRIMARY KEY (id);


--
-- TOC entry 1952 (class 2606 OID 663137)
-- Dependencies: 170 170
-- Name: links_address_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY links
    ADD CONSTRAINT links_address_key UNIQUE (address);


--
-- TOC entry 1954 (class 2606 OID 16474)
-- Dependencies: 170 170
-- Name: links_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY links
    ADD CONSTRAINT links_pkey PRIMARY KEY (id);


--
-- TOC entry 1960 (class 2606 OID 122740)
-- Dependencies: 174 174
-- Name: listings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY listings
    ADD CONSTRAINT listings_pkey PRIMARY KEY (id);


--
-- TOC entry 1956 (class 2606 OID 114066)
-- Dependencies: 172 172
-- Name: lists_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY lists
    ADD CONSTRAINT lists_name_key UNIQUE (name);


--
-- TOC entry 1958 (class 2606 OID 114064)
-- Dependencies: 172 172
-- Name: lists_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY lists
    ADD CONSTRAINT lists_pkey PRIMARY KEY (id);


--
-- TOC entry 1944 (class 2606 OID 22834)
-- Dependencies: 166 166
-- Name: messages_msgid_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_msgid_key UNIQUE (msgid);


--
-- TOC entry 1946 (class 2606 OID 16430)
-- Dependencies: 166 166
-- Name: messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- TOC entry 1962 (class 2606 OID 129564)
-- Dependencies: 176 176
-- Name: process_status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY process_status
    ADD CONSTRAINT process_status_pkey PRIMARY KEY (id);


--
-- TOC entry 1948 (class 2606 OID 16453)
-- Dependencies: 168 168
-- Name: subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- TOC entry 1950 (class 2606 OID 790075)
-- Dependencies: 168 168 168
-- Name: subscriptions_target_subscriber_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY subscriptions
    ADD CONSTRAINT subscriptions_target_subscriber_key UNIQUE (target, subscriber);


--
-- TOC entry 1942 (class 1259 OID 798343)
-- Dependencies: 166 166 166
-- Name: messages_destination_processed_id_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX messages_destination_processed_id_idx ON messages USING btree (destination, processed, id);


--
-- TOC entry 1965 (class 2606 OID 16441)
-- Dependencies: 164 1940 162
-- Name: addresses_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY addresses
    ADD CONSTRAINT addresses_domain_fkey FOREIGN KEY (domain) REFERENCES domains(id);


--
-- TOC entry 1966 (class 2606 OID 347392)
-- Dependencies: 162 1936 162
-- Name: addresses_group_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY addresses
    ADD CONSTRAINT addresses_group_fkey FOREIGN KEY ("group") REFERENCES addresses(id);


--
-- TOC entry 1978 (class 2606 OID 798333)
-- Dependencies: 1940 164 182
-- Name: lastsent_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY lastsent
    ADD CONSTRAINT lastsent_domain_fkey FOREIGN KEY (domain) REFERENCES domains(id);


--
-- TOC entry 1979 (class 2606 OID 798338)
-- Dependencies: 166 1945 182
-- Name: lastsent_lastsent_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY lastsent
    ADD CONSTRAINT lastsent_lastsent_fkey FOREIGN KEY (lastsent) REFERENCES messages(id);


--
-- TOC entry 1977 (class 2606 OID 798328)
-- Dependencies: 162 1936 182
-- Name: lastsent_subscriber_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY lastsent
    ADD CONSTRAINT lastsent_subscriber_fkey FOREIGN KEY (subscriber) REFERENCES addresses(id);


--
-- TOC entry 1974 (class 2606 OID 16475)
-- Dependencies: 1936 162 170
-- Name: links_address_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY links
    ADD CONSTRAINT links_address_fkey FOREIGN KEY (address) REFERENCES addresses(id);


--
-- TOC entry 1975 (class 2606 OID 339199)
-- Dependencies: 1936 162 174
-- Name: listings_address_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY listings
    ADD CONSTRAINT listings_address_fkey FOREIGN KEY (address) REFERENCES addresses(id);


--
-- TOC entry 1976 (class 2606 OID 339204)
-- Dependencies: 1957 172 174
-- Name: listings_list_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY listings
    ADD CONSTRAINT listings_list_fkey FOREIGN KEY (list) REFERENCES lists(id);


--
-- TOC entry 1968 (class 2606 OID 16436)
-- Dependencies: 166 1936 162
-- Name: messages_destination_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_destination_fkey FOREIGN KEY (destination) REFERENCES addresses(id);


--
-- TOC entry 1969 (class 2606 OID 331779)
-- Dependencies: 166 1961 176
-- Name: messages_processed_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_processed_fkey FOREIGN KEY (processed) REFERENCES process_status(id);


--
-- TOC entry 1970 (class 2606 OID 764619)
-- Dependencies: 166 1936 162
-- Name: messages_receivedfrom_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_receivedfrom_fkey FOREIGN KEY (receivedfrom) REFERENCES addresses(id);


--
-- TOC entry 1967 (class 2606 OID 16431)
-- Dependencies: 166 1936 162
-- Name: messages_source_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_source_fkey FOREIGN KEY (source) REFERENCES addresses(id);


--
-- TOC entry 1972 (class 2606 OID 339194)
-- Dependencies: 1945 166 168
-- Name: subscriptions_lastsent_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY subscriptions
    ADD CONSTRAINT subscriptions_lastsent_fkey FOREIGN KEY (lastsent) REFERENCES messages(id);


--
-- TOC entry 1973 (class 2606 OID 667080)
-- Dependencies: 162 1936 168
-- Name: subscriptions_subscriber_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY subscriptions
    ADD CONSTRAINT subscriptions_subscriber_fkey FOREIGN KEY (subscriber) REFERENCES addresses(id);


--
-- TOC entry 1971 (class 2606 OID 16454)
-- Dependencies: 162 1936 168
-- Name: subscriptions_target_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY subscriptions
    ADD CONSTRAINT subscriptions_target_fkey FOREIGN KEY (target) REFERENCES addresses(id);


--
-- TOC entry 1984 (class 0 OID 0)
-- Dependencies: 5
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- TOC entry 1986 (class 0 OID 0)
-- Dependencies: 162
-- Name: addresses; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE addresses FROM PUBLIC;
REVOKE ALL ON TABLE addresses FROM postgres;
GRANT ALL ON TABLE addresses TO postgres;
GRANT SELECT,INSERT,UPDATE ON TABLE addresses TO fido;


--
-- TOC entry 1988 (class 0 OID 0)
-- Dependencies: 161
-- Name: addresses_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE addresses_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE addresses_id_seq FROM postgres;
GRANT ALL ON SEQUENCE addresses_id_seq TO postgres;
GRANT UPDATE ON SEQUENCE addresses_id_seq TO fido;


--
-- TOC entry 1990 (class 0 OID 0)
-- Dependencies: 164
-- Name: domains; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE domains FROM PUBLIC;
REVOKE ALL ON TABLE domains FROM postgres;
GRANT ALL ON TABLE domains TO postgres;
GRANT SELECT ON TABLE domains TO fido;


--
-- TOC entry 1993 (class 0 OID 0)
-- Dependencies: 170
-- Name: links; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE links FROM PUBLIC;
REVOKE ALL ON TABLE links FROM postgres;
GRANT ALL ON TABLE links TO postgres;
GRANT SELECT,INSERT,UPDATE ON TABLE links TO fido;


--
-- TOC entry 1995 (class 0 OID 0)
-- Dependencies: 169
-- Name: links_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE links_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE links_id_seq FROM postgres;
GRANT ALL ON SEQUENCE links_id_seq TO postgres;
GRANT UPDATE ON SEQUENCE links_id_seq TO fido;


--
-- TOC entry 1998 (class 0 OID 0)
-- Dependencies: 166
-- Name: messages; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE messages FROM PUBLIC;
REVOKE ALL ON TABLE messages FROM postgres;
GRANT ALL ON TABLE messages TO postgres;
GRANT SELECT,INSERT,UPDATE ON TABLE messages TO fido;


--
-- TOC entry 2000 (class 0 OID 0)
-- Dependencies: 165
-- Name: messages_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE messages_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE messages_id_seq FROM postgres;
GRANT ALL ON SEQUENCE messages_id_seq TO postgres;
GRANT UPDATE ON SEQUENCE messages_id_seq TO fido;


--
-- TOC entry 2003 (class 0 OID 0)
-- Dependencies: 168
-- Name: subscriptions; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE subscriptions FROM PUBLIC;
REVOKE ALL ON TABLE subscriptions FROM postgres;
GRANT ALL ON TABLE subscriptions TO postgres;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE subscriptions TO fido;


--
-- TOC entry 2005 (class 0 OID 0)
-- Dependencies: 167
-- Name: subscriptions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE subscriptions_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE subscriptions_id_seq FROM postgres;
GRANT ALL ON SEQUENCE subscriptions_id_seq TO postgres;
GRANT UPDATE ON SEQUENCE subscriptions_id_seq TO fido;


-- Completed on 2012-01-22 18:14:51 MSK

--
-- PostgreSQL database dump complete
--

