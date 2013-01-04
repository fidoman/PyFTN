--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
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
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
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
-- Name: addresses; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE addresses (
    id bigint NOT NULL,
    domain integer,
    text character varying,
    owner character varying,
    "group" bigint,
    last bigint
);


ALTER TABLE public.addresses OWNER TO postgres;

--
-- Name: COLUMN addresses.last; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN addresses.last IS 'Last message sent to this address.
Introduced to improve export times.';


--
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
-- Name: addresses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE addresses_id_seq OWNED BY addresses.id;


--
-- Name: deletedvitalsubscriptionwatermarks; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE deletedvitalsubscriptionwatermarks (
    id bigint NOT NULL,
    target bigint,
    message bigint
);


ALTER TABLE public.deletedvitalsubscriptionwatermarks OWNER TO postgres;

--
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
-- Name: deletedvitalsubscriptionwatermarks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE deletedvitalsubscriptionwatermarks_id_seq OWNED BY deletedvitalsubscriptionwatermarks.id;


--
-- Name: domains; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE domains (
    id integer NOT NULL,
    name character varying NOT NULL,
    verifysubscriptions boolean
);


ALTER TABLE public.domains OWNER TO postgres;

--
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
-- Name: domains_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE domains_id_seq OWNED BY domains.id;


--
-- Name: files; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE files (
    id bigint NOT NULL,
    length bigint,
    crc32 character(8),
    sha256 character(64),
    firstseenas character varying
);


ALTER TABLE public.files OWNER TO postgres;

--
-- Name: files_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.files_id_seq OWNER TO postgres;

--
-- Name: files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE files_id_seq OWNED BY files.id;


--
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
-- Name: lastsent_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE lastsent_id_seq OWNED BY lastsent.id;


--
-- Name: links; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE links (
    id bigint NOT NULL,
    address bigint,
    authentication xml,
    connection xml,
    pktn bigint DEFAULT 0 NOT NULL,
    bundlen bigint DEFAULT 0 NOT NULL,
    ticn bigint DEFAULT 0 NOT NULL,
    pktformat character varying DEFAULT 'pkt2'::character varying,
    bundle character varying DEFAULT 'zip'::character varying
);


ALTER TABLE public.links OWNER TO postgres;

--
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
-- Name: links_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE links_id_seq OWNED BY links.id;


--
-- Name: links_simple; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW links_simple AS
    SELECT l.domain AS link_domain, l.text AS link_address, links.authentication, links.connection FROM links, addresses l WHERE (l.id = links.address);


ALTER TABLE public.links_simple OWNER TO postgres;

--
-- Name: listings; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE listings (
    id bigint NOT NULL,
    address bigint,
    list bigint
);


ALTER TABLE public.listings OWNER TO postgres;

--
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
-- Name: listings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE listings_id_seq OWNED BY listings.id;


--
-- Name: lists; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE lists (
    id bigint NOT NULL,
    name character varying
);


ALTER TABLE public.lists OWNER TO postgres;

--
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
-- Name: lists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE lists_id_seq OWNED BY lists.id;


--
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
    receivedfrom bigint,
    origcharset character varying,
    receivedtimestamp timestamp with time zone
);


ALTER TABLE public.messages OWNER TO postgres;

--
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
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE messages_id_seq OWNED BY messages.id;


--
-- Name: messages_simple; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW messages_simple AS
    SELECT f.domain AS from_domain, f.text AS from_address, t.domain AS to_domain, t.text AS to_address, m.header, m.body, m.processed, m.msgid, m.receivedfrom FROM messages m, addresses f, addresses t WHERE ((t.id = m.destination) AND (f.id = m.source)) ORDER BY m.id;


ALTER TABLE public.messages_simple OWNER TO postgres;

--
-- Name: msgid_seq; Type: SEQUENCE; Schema: public; Owner: fido
--

CREATE SEQUENCE msgid_seq
    START WITH 1330764251
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.msgid_seq OWNER TO fido;

--
-- Name: process_status; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE process_status (
    id integer NOT NULL,
    name character varying
);


ALTER TABLE public.process_status OWNER TO postgres;

--
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
-- Name: process_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE process_status_id_seq OWNED BY process_status.id;


--
-- Name: receivedfiles; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE receivedfiles (
    id bigint NOT NULL,
    "from" bigint,
    file bigint,
    name character varying,
    "time" timestamp with time zone
);


ALTER TABLE public.receivedfiles OWNER TO postgres;

--
-- Name: receivedfiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE receivedfiles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.receivedfiles_id_seq OWNER TO postgres;

--
-- Name: receivedfiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE receivedfiles_id_seq OWNED BY receivedfiles.id;


--
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
-- Name: COLUMN subscriptions.vital; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN subscriptions.vital IS 'tossing message without vital subscription (uplink for echo, nexthop for netmail) must fail ';


--
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
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE subscriptions_id_seq OWNED BY subscriptions.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY addresses ALTER COLUMN id SET DEFAULT nextval('addresses_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY deletedvitalsubscriptionwatermarks ALTER COLUMN id SET DEFAULT nextval('deletedvitalsubscriptionwatermarks_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY domains ALTER COLUMN id SET DEFAULT nextval('domains_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY files ALTER COLUMN id SET DEFAULT nextval('files_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY lastsent ALTER COLUMN id SET DEFAULT nextval('lastsent_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY links ALTER COLUMN id SET DEFAULT nextval('links_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY listings ALTER COLUMN id SET DEFAULT nextval('listings_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY lists ALTER COLUMN id SET DEFAULT nextval('lists_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages ALTER COLUMN id SET DEFAULT nextval('messages_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY process_status ALTER COLUMN id SET DEFAULT nextval('process_status_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY receivedfiles ALTER COLUMN id SET DEFAULT nextval('receivedfiles_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY subscriptions ALTER COLUMN id SET DEFAULT nextval('subscriptions_id_seq'::regclass);


--
-- Name: addresses_domain_text_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY addresses
    ADD CONSTRAINT addresses_domain_text_key UNIQUE (domain, text);


--
-- Name: addresses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (id);


--
-- Name: deletedvitalsubscriptionwatermarks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY deletedvitalsubscriptionwatermarks
    ADD CONSTRAINT deletedvitalsubscriptionwatermarks_pkey PRIMARY KEY (id);


--
-- Name: deletedvitalsubscriptionwatermarks_target_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY deletedvitalsubscriptionwatermarks
    ADD CONSTRAINT deletedvitalsubscriptionwatermarks_target_key UNIQUE (target);


--
-- Name: domains_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY domains
    ADD CONSTRAINT domains_name_key UNIQUE (name);


--
-- Name: domains_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY domains
    ADD CONSTRAINT domains_pkey PRIMARY KEY (id);


--
-- Name: files_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: lastsent_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY lastsent
    ADD CONSTRAINT lastsent_pkey PRIMARY KEY (id);


--
-- Name: links_address_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY links
    ADD CONSTRAINT links_address_key UNIQUE (address);


--
-- Name: links_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY links
    ADD CONSTRAINT links_pkey PRIMARY KEY (id);


--
-- Name: listings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY listings
    ADD CONSTRAINT listings_pkey PRIMARY KEY (id);


--
-- Name: lists_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY lists
    ADD CONSTRAINT lists_name_key UNIQUE (name);


--
-- Name: lists_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY lists
    ADD CONSTRAINT lists_pkey PRIMARY KEY (id);


--
-- Name: messages_msgid_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_msgid_key UNIQUE (msgid);


--
-- Name: messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: process_status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY process_status
    ADD CONSTRAINT process_status_pkey PRIMARY KEY (id);


--
-- Name: receivedfiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY receivedfiles
    ADD CONSTRAINT receivedfiles_pkey PRIMARY KEY (id);


--
-- Name: subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: subscriptions_target_subscriber_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY subscriptions
    ADD CONSTRAINT subscriptions_target_subscriber_key UNIQUE (target, subscriber);


--
-- Name: addresses_group_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX addresses_group_idx ON addresses USING btree ("group");


--
-- Name: messages_destination_id_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX messages_destination_id_idx ON messages USING btree (destination, id DESC);


--
-- Name: messages_destination_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX messages_destination_idx ON messages USING btree (destination);


--
-- Name: messages_destination_processed_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX messages_destination_processed_idx ON messages USING btree (destination, processed);


--
-- Name: subscriptions_subscriber_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX subscriptions_subscriber_idx ON subscriptions USING btree (subscriber);


--
-- Name: addresses_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY addresses
    ADD CONSTRAINT addresses_domain_fkey FOREIGN KEY (domain) REFERENCES domains(id);


--
-- Name: addresses_group_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY addresses
    ADD CONSTRAINT addresses_group_fkey FOREIGN KEY ("group") REFERENCES addresses(id);


--
-- Name: deletedvitalsubscriptionwatermarks_message_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY deletedvitalsubscriptionwatermarks
    ADD CONSTRAINT deletedvitalsubscriptionwatermarks_message_fkey FOREIGN KEY (message) REFERENCES messages(id);


--
-- Name: deletedvitalsubscriptionwatermarks_target_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY deletedvitalsubscriptionwatermarks
    ADD CONSTRAINT deletedvitalsubscriptionwatermarks_target_fkey FOREIGN KEY (target) REFERENCES addresses(id);


--
-- Name: lastsent_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY lastsent
    ADD CONSTRAINT lastsent_domain_fkey FOREIGN KEY (domain) REFERENCES domains(id);


--
-- Name: lastsent_lastsent_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY lastsent
    ADD CONSTRAINT lastsent_lastsent_fkey FOREIGN KEY (lastsent) REFERENCES messages(id);


--
-- Name: lastsent_subscriber_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY lastsent
    ADD CONSTRAINT lastsent_subscriber_fkey FOREIGN KEY (subscriber) REFERENCES addresses(id);


--
-- Name: links_address_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY links
    ADD CONSTRAINT links_address_fkey FOREIGN KEY (address) REFERENCES addresses(id);


--
-- Name: listings_address_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY listings
    ADD CONSTRAINT listings_address_fkey FOREIGN KEY (address) REFERENCES addresses(id);


--
-- Name: listings_list_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY listings
    ADD CONSTRAINT listings_list_fkey FOREIGN KEY (list) REFERENCES lists(id);


--
-- Name: messages_destination_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_destination_fkey FOREIGN KEY (destination) REFERENCES addresses(id);


--
-- Name: messages_processed_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_processed_fkey FOREIGN KEY (processed) REFERENCES process_status(id);


--
-- Name: messages_receivedfrom_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_receivedfrom_fkey FOREIGN KEY (receivedfrom) REFERENCES addresses(id);


--
-- Name: messages_source_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_source_fkey FOREIGN KEY (source) REFERENCES addresses(id);


--
-- Name: receivedfiles_file_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY receivedfiles
    ADD CONSTRAINT receivedfiles_file_fkey FOREIGN KEY (file) REFERENCES files(id);


--
-- Name: receivedfiles_from_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY receivedfiles
    ADD CONSTRAINT receivedfiles_from_fkey FOREIGN KEY ("from") REFERENCES addresses(id);


--
-- Name: subscriptions_subscriber_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY subscriptions
    ADD CONSTRAINT subscriptions_subscriber_fkey FOREIGN KEY (subscriber) REFERENCES addresses(id);


--
-- Name: subscriptions_target_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY subscriptions
    ADD CONSTRAINT subscriptions_target_fkey FOREIGN KEY (target) REFERENCES addresses(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: addresses; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE addresses FROM PUBLIC;
REVOKE ALL ON TABLE addresses FROM postgres;
GRANT ALL ON TABLE addresses TO postgres;
GRANT SELECT,INSERT,UPDATE ON TABLE addresses TO fido;


--
-- Name: addresses_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE addresses_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE addresses_id_seq FROM postgres;
GRANT ALL ON SEQUENCE addresses_id_seq TO postgres;
GRANT UPDATE ON SEQUENCE addresses_id_seq TO fido;


--
-- Name: deletedvitalsubscriptionwatermarks; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE deletedvitalsubscriptionwatermarks FROM PUBLIC;
REVOKE ALL ON TABLE deletedvitalsubscriptionwatermarks FROM postgres;
GRANT ALL ON TABLE deletedvitalsubscriptionwatermarks TO postgres;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE deletedvitalsubscriptionwatermarks TO fido;


--
-- Name: deletedvitalsubscriptionwatermarks_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE deletedvitalsubscriptionwatermarks_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE deletedvitalsubscriptionwatermarks_id_seq FROM postgres;
GRANT ALL ON SEQUENCE deletedvitalsubscriptionwatermarks_id_seq TO postgres;
GRANT UPDATE ON SEQUENCE deletedvitalsubscriptionwatermarks_id_seq TO fido;


--
-- Name: domains; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE domains FROM PUBLIC;
REVOKE ALL ON TABLE domains FROM postgres;
GRANT ALL ON TABLE domains TO postgres;
GRANT SELECT ON TABLE domains TO fido;


--
-- Name: files; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE files FROM PUBLIC;
REVOKE ALL ON TABLE files FROM postgres;
GRANT ALL ON TABLE files TO postgres;
GRANT SELECT,INSERT ON TABLE files TO PUBLIC;


--
-- Name: links; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE links FROM PUBLIC;
REVOKE ALL ON TABLE links FROM postgres;
GRANT ALL ON TABLE links TO postgres;
GRANT SELECT,INSERT,UPDATE ON TABLE links TO fido;


--
-- Name: links_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE links_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE links_id_seq FROM postgres;
GRANT ALL ON SEQUENCE links_id_seq TO postgres;
GRANT UPDATE ON SEQUENCE links_id_seq TO fido;


--
-- Name: messages; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE messages FROM PUBLIC;
REVOKE ALL ON TABLE messages FROM postgres;
GRANT ALL ON TABLE messages TO postgres;
GRANT SELECT,INSERT,UPDATE ON TABLE messages TO fido;


--
-- Name: messages_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE messages_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE messages_id_seq FROM postgres;
GRANT ALL ON SEQUENCE messages_id_seq TO postgres;
GRANT UPDATE ON SEQUENCE messages_id_seq TO fido;


--
-- Name: subscriptions; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE subscriptions FROM PUBLIC;
REVOKE ALL ON TABLE subscriptions FROM postgres;
GRANT ALL ON TABLE subscriptions TO postgres;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE subscriptions TO fido;


--
-- Name: subscriptions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE subscriptions_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE subscriptions_id_seq FROM postgres;
GRANT ALL ON SEQUENCE subscriptions_id_seq TO postgres;
GRANT UPDATE ON SEQUENCE subscriptions_id_seq TO fido;


--
-- PostgreSQL database dump complete
--

