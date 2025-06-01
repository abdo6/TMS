--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: affretement; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.affretement (
    id_affretement integer NOT NULL,
    date_demande date NOT NULL,
    date_debut_souhaitee date NOT NULL,
    date_fin_souhaitee date NOT NULL,
    description_besoin character varying(500) NOT NULL,
    statut character varying(50) NOT NULL,
    cout_estime numeric(10,2),
    id_detail_commande integer,
    id_sous_traitant integer,
    id_vehicule_externe integer,
    id_chauffeur_externe integer
);


ALTER TABLE public.affretement OWNER TO tms_user;

--
-- Name: affretement_id_affretement_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.affretement_id_affretement_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.affretement_id_affretement_seq OWNER TO tms_user;

--
-- Name: affretement_id_affretement_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.affretement_id_affretement_seq OWNED BY public.affretement.id_affretement;


--
-- Name: chauffeur; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.chauffeur (
    id_chauffeur integer NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100) NOT NULL,
    adresse character varying(255),
    numero_telephone character varying(20),
    email character varying(120),
    categorie_ch character varying(50)
);


ALTER TABLE public.chauffeur OWNER TO tms_user;

--
-- Name: chauffeur_externe; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.chauffeur_externe (
    id_chauffeur_externe integer NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100) NOT NULL,
    numero_telephone character varying(20),
    email character varying(120),
    categorie_permis character varying(50),
    id_sous_traitant integer NOT NULL
);


ALTER TABLE public.chauffeur_externe OWNER TO tms_user;

--
-- Name: chauffeur_externe_id_chauffeur_externe_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.chauffeur_externe_id_chauffeur_externe_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chauffeur_externe_id_chauffeur_externe_seq OWNER TO tms_user;

--
-- Name: chauffeur_externe_id_chauffeur_externe_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.chauffeur_externe_id_chauffeur_externe_seq OWNED BY public.chauffeur_externe.id_chauffeur_externe;


--
-- Name: chauffeur_id_chauffeur_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.chauffeur_id_chauffeur_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chauffeur_id_chauffeur_seq OWNER TO tms_user;

--
-- Name: chauffeur_id_chauffeur_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.chauffeur_id_chauffeur_seq OWNED BY public.chauffeur.id_chauffeur;


--
-- Name: client_final; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.client_final (
    id_client_final integer NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100),
    adresse character varying(255),
    numero_telephone character varying(20),
    email character varying(120),
    id_client_initial integer NOT NULL
);


ALTER TABLE public.client_final OWNER TO tms_user;

--
-- Name: client_final_id_client_final_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.client_final_id_client_final_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.client_final_id_client_final_seq OWNER TO tms_user;

--
-- Name: client_final_id_client_final_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.client_final_id_client_final_seq OWNED BY public.client_final.id_client_final;


--
-- Name: client_initial; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.client_initial (
    id_client_initial integer NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100),
    adresse character varying(255),
    numero_telephone character varying(20),
    email character varying(120)
);


ALTER TABLE public.client_initial OWNER TO tms_user;

--
-- Name: client_initial_id_client_initial_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.client_initial_id_client_initial_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.client_initial_id_client_initial_seq OWNER TO tms_user;

--
-- Name: client_initial_id_client_initial_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.client_initial_id_client_initial_seq OWNED BY public.client_initial.id_client_initial;


--
-- Name: date_cv; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.date_cv (
    id_date_cv integer NOT NULL,
    date_debut date NOT NULL,
    date_fin date NOT NULL,
    description character varying(255),
    id_chauffeur integer NOT NULL
);


ALTER TABLE public.date_cv OWNER TO tms_user;

--
-- Name: date_cv_id_date_cv_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.date_cv_id_date_cv_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.date_cv_id_date_cv_seq OWNER TO tms_user;

--
-- Name: date_cv_id_date_cv_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.date_cv_id_date_cv_seq OWNED BY public.date_cv.id_date_cv;


--
-- Name: date_tr; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.date_tr (
    id_date_tr integer NOT NULL,
    date_debut date NOT NULL,
    date_fin date NOT NULL,
    description character varying(255),
    id_vehicule integer NOT NULL
);


ALTER TABLE public.date_tr OWNER TO tms_user;

--
-- Name: date_tr_id_date_tr_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.date_tr_id_date_tr_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.date_tr_id_date_tr_seq OWNER TO tms_user;

--
-- Name: date_tr_id_date_tr_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.date_tr_id_date_tr_seq OWNED BY public.date_tr.id_date_tr;


--
-- Name: destination; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.destination (
    id_destination integer NOT NULL,
    latitude numeric(10,7) NOT NULL,
    longitude numeric(10,7) NOT NULL,
    description character varying(255),
    id_ville integer,
    id_province integer
);


ALTER TABLE public.destination OWNER TO tms_user;

--
-- Name: destination_id_destination_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.destination_id_destination_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.destination_id_destination_seq OWNER TO tms_user;

--
-- Name: destination_id_destination_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.destination_id_destination_seq OWNED BY public.destination.id_destination;


--
-- Name: detail_commande; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.detail_commande (
    id_detail_commande integer NOT NULL,
    quantite integer NOT NULL,
    description_colis character varying(255),
    volume numeric(10,2),
    poids numeric(10,2),
    id_entete_commande integer NOT NULL,
    id_type_vehicule integer NOT NULL,
    id_client_final integer NOT NULL,
    id_destination integer NOT NULL
);


ALTER TABLE public.detail_commande OWNER TO tms_user;

--
-- Name: detail_commande_id_detail_commande_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.detail_commande_id_detail_commande_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.detail_commande_id_detail_commande_seq OWNER TO tms_user;

--
-- Name: detail_commande_id_detail_commande_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.detail_commande_id_detail_commande_seq OWNED BY public.detail_commande.id_detail_commande;


--
-- Name: entete_commande; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.entete_commande (
    id_entete_commande integer NOT NULL,
    reference character varying(100) NOT NULL,
    date_commande date NOT NULL,
    id_client_initial integer NOT NULL,
    id_service integer NOT NULL
);


ALTER TABLE public.entete_commande OWNER TO tms_user;

--
-- Name: entete_commande_id_entete_commande_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.entete_commande_id_entete_commande_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.entete_commande_id_entete_commande_seq OWNER TO tms_user;

--
-- Name: entete_commande_id_entete_commande_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.entete_commande_id_entete_commande_seq OWNED BY public.entete_commande.id_entete_commande;


--
-- Name: feuille_de_route; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.feuille_de_route (
    id_feuille_de_route integer NOT NULL,
    description character varying(255),
    date_depart_prevu date NOT NULL,
    heure_depart_prevu time without time zone NOT NULL,
    date_arrivee_prevue date NOT NULL,
    heure_arrivee_prevue time without time zone NOT NULL,
    date_depart_reel date,
    heure_depart_reel time without time zone,
    date_arrivee_reelle date,
    heure_arrivee_reelle time without time zone,
    km_debut numeric(10,2),
    km_fin numeric(10,2),
    id_chauffeur integer NOT NULL,
    id_vehicule integer NOT NULL
);


ALTER TABLE public.feuille_de_route OWNER TO tms_user;

--
-- Name: feuille_de_route_id_feuille_de_route_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.feuille_de_route_id_feuille_de_route_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.feuille_de_route_id_feuille_de_route_seq OWNER TO tms_user;

--
-- Name: feuille_de_route_id_feuille_de_route_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.feuille_de_route_id_feuille_de_route_seq OWNED BY public.feuille_de_route.id_feuille_de_route;


--
-- Name: indisponibilite_chauffeur; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.indisponibilite_chauffeur (
    id_indispo_chauffeur integer NOT NULL,
    date_debut date NOT NULL,
    date_fin date NOT NULL,
    description character varying(255),
    id_chauffeur integer NOT NULL,
    id_type_indispo_chauffeur integer NOT NULL
);


ALTER TABLE public.indisponibilite_chauffeur OWNER TO tms_user;

--
-- Name: indisponibilite_chauffeur_id_indispo_chauffeur_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.indisponibilite_chauffeur_id_indispo_chauffeur_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.indisponibilite_chauffeur_id_indispo_chauffeur_seq OWNER TO tms_user;

--
-- Name: indisponibilite_chauffeur_id_indispo_chauffeur_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.indisponibilite_chauffeur_id_indispo_chauffeur_seq OWNED BY public.indisponibilite_chauffeur.id_indispo_chauffeur;


--
-- Name: indisponibilite_vehicule; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.indisponibilite_vehicule (
    id_indispo_vehicule integer NOT NULL,
    date_debut date NOT NULL,
    date_fin date NOT NULL,
    description character varying(255),
    id_vehicule integer NOT NULL,
    id_type_indispo_vehicule integer NOT NULL
);


ALTER TABLE public.indisponibilite_vehicule OWNER TO tms_user;

--
-- Name: indisponibilite_vehicule_id_indispo_vehicule_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.indisponibilite_vehicule_id_indispo_vehicule_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.indisponibilite_vehicule_id_indispo_vehicule_seq OWNER TO tms_user;

--
-- Name: indisponibilite_vehicule_id_indispo_vehicule_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.indisponibilite_vehicule_id_indispo_vehicule_seq OWNED BY public.indisponibilite_vehicule.id_indispo_vehicule;


--
-- Name: mission; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.mission (
    id_mission integer NOT NULL,
    date_debut date NOT NULL,
    date_fin date NOT NULL,
    heure_debut time without time zone NOT NULL,
    heure_fin time without time zone NOT NULL,
    id_chauffeur integer NOT NULL,
    id_vehicule integer NOT NULL,
    id_destination integer,
    id_feuille_de_route integer
);


ALTER TABLE public.mission OWNER TO tms_user;

--
-- Name: mission_detail; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.mission_detail (
    id_mission integer NOT NULL,
    id_detail_commande integer NOT NULL,
    ordre_livraison integer
);


ALTER TABLE public.mission_detail OWNER TO tms_user;

--
-- Name: mission_id_mission_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.mission_id_mission_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mission_id_mission_seq OWNER TO tms_user;

--
-- Name: mission_id_mission_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.mission_id_mission_seq OWNED BY public.mission.id_mission;


--
-- Name: province; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.province (
    id_province integer NOT NULL,
    nom_province character varying(100) NOT NULL,
    id_ville integer NOT NULL
);


ALTER TABLE public.province OWNER TO tms_user;

--
-- Name: province_id_province_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.province_id_province_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.province_id_province_seq OWNER TO tms_user;

--
-- Name: province_id_province_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.province_id_province_seq OWNED BY public.province.id_province;


--
-- Name: service_client; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.service_client (
    id_service integer NOT NULL,
    nom_service character varying(100) NOT NULL,
    id_client_initial integer NOT NULL
);


ALTER TABLE public.service_client OWNER TO tms_user;

--
-- Name: service_client_id_service_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.service_client_id_service_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_client_id_service_seq OWNER TO tms_user;

--
-- Name: service_client_id_service_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.service_client_id_service_seq OWNED BY public.service_client.id_service;


--
-- Name: sous_traitant; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.sous_traitant (
    id_sous_traitant integer NOT NULL,
    nom_entreprise character varying(255) NOT NULL,
    contact_personne character varying(100),
    numero_telephone character varying(20),
    email character varying(120),
    adresse character varying(255)
);


ALTER TABLE public.sous_traitant OWNER TO tms_user;

--
-- Name: sous_traitant_id_sous_traitant_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.sous_traitant_id_sous_traitant_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sous_traitant_id_sous_traitant_seq OWNER TO tms_user;

--
-- Name: sous_traitant_id_sous_traitant_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.sous_traitant_id_sous_traitant_seq OWNED BY public.sous_traitant.id_sous_traitant;


--
-- Name: trajet; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.trajet (
    id_trajet integer NOT NULL,
    distance_km numeric(10,2),
    duree_heures numeric(10,2),
    description character varying(255),
    id_destination integer NOT NULL
);


ALTER TABLE public.trajet OWNER TO tms_user;

--
-- Name: trajet_id_trajet_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.trajet_id_trajet_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trajet_id_trajet_seq OWNER TO tms_user;

--
-- Name: trajet_id_trajet_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.trajet_id_trajet_seq OWNED BY public.trajet.id_trajet;


--
-- Name: type_indispo_chauffeur; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.type_indispo_chauffeur (
    id_type_indispo_chauffeur integer NOT NULL,
    nom_type character varying(100) NOT NULL
);


ALTER TABLE public.type_indispo_chauffeur OWNER TO tms_user;

--
-- Name: type_indispo_chauffeur_id_type_indispo_chauffeur_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.type_indispo_chauffeur_id_type_indispo_chauffeur_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.type_indispo_chauffeur_id_type_indispo_chauffeur_seq OWNER TO tms_user;

--
-- Name: type_indispo_chauffeur_id_type_indispo_chauffeur_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.type_indispo_chauffeur_id_type_indispo_chauffeur_seq OWNED BY public.type_indispo_chauffeur.id_type_indispo_chauffeur;


--
-- Name: type_indispo_vehicule; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.type_indispo_vehicule (
    id_type_indispo_vehicule integer NOT NULL,
    nom_type character varying(100) NOT NULL
);


ALTER TABLE public.type_indispo_vehicule OWNER TO tms_user;

--
-- Name: type_indispo_vehicule_id_type_indispo_vehicule_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.type_indispo_vehicule_id_type_indispo_vehicule_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.type_indispo_vehicule_id_type_indispo_vehicule_seq OWNER TO tms_user;

--
-- Name: type_indispo_vehicule_id_type_indispo_vehicule_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.type_indispo_vehicule_id_type_indispo_vehicule_seq OWNED BY public.type_indispo_vehicule.id_type_indispo_vehicule;


--
-- Name: type_vehicule; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.type_vehicule (
    id_type_vehicule integer NOT NULL,
    nom_type character varying(100) NOT NULL
);


ALTER TABLE public.type_vehicule OWNER TO tms_user;

--
-- Name: type_vehicule_id_type_vehicule_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.type_vehicule_id_type_vehicule_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.type_vehicule_id_type_vehicule_seq OWNER TO tms_user;

--
-- Name: type_vehicule_id_type_vehicule_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.type_vehicule_id_type_vehicule_seq OWNED BY public.type_vehicule.id_type_vehicule;


--
-- Name: users; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(256) NOT NULL,
    role character varying(50) NOT NULL
);


ALTER TABLE public.users OWNER TO tms_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO tms_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vehicule; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.vehicule (
    id_vehicule integer NOT NULL,
    immatriculation_ve character varying(50) NOT NULL,
    categorie character varying(100)
);


ALTER TABLE public.vehicule OWNER TO tms_user;

--
-- Name: vehicule_externe; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.vehicule_externe (
    id_vehicule_externe integer NOT NULL,
    immatriculation_ve character varying(50) NOT NULL,
    categorie character varying(100),
    description character varying(255),
    id_sous_traitant integer NOT NULL
);


ALTER TABLE public.vehicule_externe OWNER TO tms_user;

--
-- Name: vehicule_externe_id_vehicule_externe_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.vehicule_externe_id_vehicule_externe_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicule_externe_id_vehicule_externe_seq OWNER TO tms_user;

--
-- Name: vehicule_externe_id_vehicule_externe_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.vehicule_externe_id_vehicule_externe_seq OWNED BY public.vehicule_externe.id_vehicule_externe;


--
-- Name: vehicule_id_vehicule_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.vehicule_id_vehicule_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicule_id_vehicule_seq OWNER TO tms_user;

--
-- Name: vehicule_id_vehicule_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.vehicule_id_vehicule_seq OWNED BY public.vehicule.id_vehicule;


--
-- Name: ville; Type: TABLE; Schema: public; Owner: tms_user
--

CREATE TABLE public.ville (
    id_ville integer NOT NULL,
    code_ville character varying(50) NOT NULL,
    nom_ville character varying(100) NOT NULL
);


ALTER TABLE public.ville OWNER TO tms_user;

--
-- Name: ville_id_ville_seq; Type: SEQUENCE; Schema: public; Owner: tms_user
--

CREATE SEQUENCE public.ville_id_ville_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ville_id_ville_seq OWNER TO tms_user;

--
-- Name: ville_id_ville_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tms_user
--

ALTER SEQUENCE public.ville_id_ville_seq OWNED BY public.ville.id_ville;


--
-- Name: affretement id_affretement; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.affretement ALTER COLUMN id_affretement SET DEFAULT nextval('public.affretement_id_affretement_seq'::regclass);


--
-- Name: chauffeur id_chauffeur; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.chauffeur ALTER COLUMN id_chauffeur SET DEFAULT nextval('public.chauffeur_id_chauffeur_seq'::regclass);


--
-- Name: chauffeur_externe id_chauffeur_externe; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.chauffeur_externe ALTER COLUMN id_chauffeur_externe SET DEFAULT nextval('public.chauffeur_externe_id_chauffeur_externe_seq'::regclass);


--
-- Name: client_final id_client_final; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.client_final ALTER COLUMN id_client_final SET DEFAULT nextval('public.client_final_id_client_final_seq'::regclass);


--
-- Name: client_initial id_client_initial; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.client_initial ALTER COLUMN id_client_initial SET DEFAULT nextval('public.client_initial_id_client_initial_seq'::regclass);


--
-- Name: date_cv id_date_cv; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.date_cv ALTER COLUMN id_date_cv SET DEFAULT nextval('public.date_cv_id_date_cv_seq'::regclass);


--
-- Name: date_tr id_date_tr; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.date_tr ALTER COLUMN id_date_tr SET DEFAULT nextval('public.date_tr_id_date_tr_seq'::regclass);


--
-- Name: destination id_destination; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.destination ALTER COLUMN id_destination SET DEFAULT nextval('public.destination_id_destination_seq'::regclass);


--
-- Name: detail_commande id_detail_commande; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.detail_commande ALTER COLUMN id_detail_commande SET DEFAULT nextval('public.detail_commande_id_detail_commande_seq'::regclass);


--
-- Name: entete_commande id_entete_commande; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.entete_commande ALTER COLUMN id_entete_commande SET DEFAULT nextval('public.entete_commande_id_entete_commande_seq'::regclass);


--
-- Name: feuille_de_route id_feuille_de_route; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.feuille_de_route ALTER COLUMN id_feuille_de_route SET DEFAULT nextval('public.feuille_de_route_id_feuille_de_route_seq'::regclass);


--
-- Name: indisponibilite_chauffeur id_indispo_chauffeur; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.indisponibilite_chauffeur ALTER COLUMN id_indispo_chauffeur SET DEFAULT nextval('public.indisponibilite_chauffeur_id_indispo_chauffeur_seq'::regclass);


--
-- Name: indisponibilite_vehicule id_indispo_vehicule; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.indisponibilite_vehicule ALTER COLUMN id_indispo_vehicule SET DEFAULT nextval('public.indisponibilite_vehicule_id_indispo_vehicule_seq'::regclass);


--
-- Name: mission id_mission; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.mission ALTER COLUMN id_mission SET DEFAULT nextval('public.mission_id_mission_seq'::regclass);


--
-- Name: province id_province; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.province ALTER COLUMN id_province SET DEFAULT nextval('public.province_id_province_seq'::regclass);


--
-- Name: service_client id_service; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.service_client ALTER COLUMN id_service SET DEFAULT nextval('public.service_client_id_service_seq'::regclass);


--
-- Name: sous_traitant id_sous_traitant; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.sous_traitant ALTER COLUMN id_sous_traitant SET DEFAULT nextval('public.sous_traitant_id_sous_traitant_seq'::regclass);


--
-- Name: trajet id_trajet; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.trajet ALTER COLUMN id_trajet SET DEFAULT nextval('public.trajet_id_trajet_seq'::regclass);


--
-- Name: type_indispo_chauffeur id_type_indispo_chauffeur; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.type_indispo_chauffeur ALTER COLUMN id_type_indispo_chauffeur SET DEFAULT nextval('public.type_indispo_chauffeur_id_type_indispo_chauffeur_seq'::regclass);


--
-- Name: type_indispo_vehicule id_type_indispo_vehicule; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.type_indispo_vehicule ALTER COLUMN id_type_indispo_vehicule SET DEFAULT nextval('public.type_indispo_vehicule_id_type_indispo_vehicule_seq'::regclass);


--
-- Name: type_vehicule id_type_vehicule; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.type_vehicule ALTER COLUMN id_type_vehicule SET DEFAULT nextval('public.type_vehicule_id_type_vehicule_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vehicule id_vehicule; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.vehicule ALTER COLUMN id_vehicule SET DEFAULT nextval('public.vehicule_id_vehicule_seq'::regclass);


--
-- Name: vehicule_externe id_vehicule_externe; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.vehicule_externe ALTER COLUMN id_vehicule_externe SET DEFAULT nextval('public.vehicule_externe_id_vehicule_externe_seq'::regclass);


--
-- Name: ville id_ville; Type: DEFAULT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.ville ALTER COLUMN id_ville SET DEFAULT nextval('public.ville_id_ville_seq'::regclass);


--
-- Data for Name: affretement; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.affretement (id_affretement, date_demande, date_debut_souhaitee, date_fin_souhaitee, description_besoin, statut, cout_estime, id_detail_commande, id_sous_traitant, id_vehicule_externe, id_chauffeur_externe) FROM stdin;
1	2025-05-25	2025-06-01	2025-06-01	Transport urgent de médicaments vers Marrakech	En attente	500.00	4	\N	\N	\N
2	2025-05-15	2025-05-20	2025-05-20	Retour de vide de Rabat	Terminé	200.00	\N	2	2	2
\.


--
-- Data for Name: chauffeur; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.chauffeur (id_chauffeur, nom, prenom, adresse, numero_telephone, email, categorie_ch) FROM stdin;
1	Benani	Ahmed	Rue Hassan II, Casablanca	0600112233	ahmed.b@example.com	C, E
2	Alaoui	Fatima	Av. Mohammed V, Rabat	0611223344	fatima.a@example.com	C
3	Cherkaoui	Youssef	Bd Zerktouni, Marrakech	0622334455	youssef.c@example.com	B, C
\.


--
-- Data for Name: chauffeur_externe; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.chauffeur_externe (id_chauffeur_externe, nom, prenom, numero_telephone, email, categorie_permis, id_sous_traitant) FROM stdin;
1	Idrissi	Khalid	0680900011	khalid.i@example.com	C, E	1
2	Amrani	Samira	0690011223	samira.a@example.com	B	2
\.


--
-- Data for Name: client_final; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.client_final (id_client_final, nom, prenom, adresse, numero_telephone, email, id_client_initial) FROM stdin;
1	Kettani	Nour	Quartier Maarif, Casablanca	0655667788	nour.k@example.com	1
2	Bennani	Omar	Hay Riad, Rabat	0666778899	omar.b@example.com	2
3	Ziani	Sarah	Gueliz, Marrakech	0677889900	sarah.z@example.com	1
\.


--
-- Data for Name: client_initial; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.client_initial (id_client_initial, nom, prenom, adresse, numero_telephone, email) FROM stdin;
1	Transport Express Maroc	Service Client	Casablanca	0522112233	contact@tem.ma
2	Logistique Sans Frontières	Commercial	Rabat	0537445566	info@lsf.ma
\.


--
-- Data for Name: date_cv; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.date_cv (id_date_cv, date_debut, date_fin, description, id_chauffeur) FROM stdin;
1	2020-10-10	2030-10-10	Permis	2
\.


--
-- Data for Name: date_tr; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.date_tr (id_date_tr, date_debut, date_fin, description, id_vehicule) FROM stdin;
1	2020-10-10	2030-10-10	Assurance	1
\.


--
-- Data for Name: destination; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.destination (id_destination, latitude, longitude, description, id_ville, id_province) FROM stdin;
1	33.5898860	-7.6038690	Centre Commercial AnfaPlace, Casablanca	1	1
2	33.6062770	-7.5350790	Zone Industrielle Ain Sebaa, Casablanca	1	1
3	34.0768650	-6.6800730	Technopolis, Rabat	2	7
4	31.6294720	-7.9810610	Médina, Marrakech	3	\N
\.


--
-- Data for Name: detail_commande; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.detail_commande (id_detail_commande, quantite, description_colis, volume, poids, id_entete_commande, id_type_vehicule, id_client_final, id_destination) FROM stdin;
1	10	Cartons de livres	2.50	150.00	1	1	1	1
2	1	Palette de produits électroniques	1.20	500.00	1	3	2	2
3	50	Sacs de ciment	5.00	2500.00	2	3	2	3
4	3	Échantillons textiles	0.50	20.00	3	1	3	4
\.


--
-- Data for Name: entete_commande; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.entete_commande (id_entete_commande, reference, date_commande, id_client_initial, id_service) FROM stdin;
1	REF-2024-001	2025-05-25	1	1
2	REF-2024-002	2025-05-25	1	2
3	REF-2024-003	2025-05-25	2	3
4	entetcommande4	2025-05-25	2	1
5	entetcommande5	2025-05-25	1	2
\.


--
-- Data for Name: feuille_de_route; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.feuille_de_route (id_feuille_de_route, description, date_depart_prevu, heure_depart_prevu, date_arrivee_prevue, heure_arrivee_prevue, date_depart_reel, heure_depart_reel, date_arrivee_reelle, heure_arrivee_reelle, km_debut, km_fin, id_chauffeur, id_vehicule) FROM stdin;
1	Tournée quotidienne Casablanca Nord	2025-05-26	08:00:00	2025-05-26	17:00:00	\N	\N	\N	\N	\N	\N	1	1
2	Livraison spéciale Rabat	2025-05-27	09:00:00	2025-05-27	14:00:00	\N	\N	\N	\N	\N	\N	2	2
\.


--
-- Data for Name: indisponibilite_chauffeur; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.indisponibilite_chauffeur (id_indispo_chauffeur, date_debut, date_fin, description, id_chauffeur, id_type_indispo_chauffeur) FROM stdin;
1	2025-06-24	2025-07-09	Congés annuels planifiés	1	1
2	2025-05-20	2025-05-27	Grippe	2	2
\.


--
-- Data for Name: indisponibilite_vehicule; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.indisponibilite_vehicule (id_indispo_vehicule, date_debut, date_fin, description, id_vehicule, id_type_indispo_vehicule) FROM stdin;
1	2025-06-04	2025-06-06	Remplacement freins	1	2
2	2025-05-22	2025-05-25	Panne de batterie	2	1
\.


--
-- Data for Name: mission; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.mission (id_mission, date_debut, date_fin, heure_debut, heure_fin, id_chauffeur, id_vehicule, id_destination, id_feuille_de_route) FROM stdin;
1	2025-05-26	2025-05-26	08:00:00	12:00:00	1	1	1	1
2	2025-05-26	2025-05-26	13:00:00	17:00:00	1	1	2	1
3	2025-05-27	2025-05-27	09:00:00	14:00:00	2	2	3	2
4	2025-10-10	2025-10-20	00:00:00	00:00:00	3	2	1	\N
\.


--
-- Data for Name: mission_detail; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.mission_detail (id_mission, id_detail_commande, ordre_livraison) FROM stdin;
1	2	\N
3	3	\N
3	4	\N
\.


--
-- Data for Name: province; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.province (id_province, nom_province, id_ville) FROM stdin;
1	Casablanca-Anfa	1
2	Ain Chock	1
3	Hay Hassani	1
4	Ben M'Sick	1
5	Mohammedia	1
6	Nouaceur	1
7	Rabat	2
8	Salé	2
9	Skhirate-Témara	2
10	Marrakech	3
11	Al Haouz	3
12	Chichaoua	3
13	Rehamna	3
14	Fès	4
15	Moulay Yacoub	4
16	Sefrou	4
17	Tanger-Assilah	5
18	Fahs-Anjra	5
19	Larache	5
20	Agadir Ida-Ou Tanane	6
21	Chtouka Ait Baha	6
22	Taroudant	6
\.


--
-- Data for Name: service_client; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.service_client (id_service, nom_service, id_client_initial) FROM stdin;
1	Expédition Nationale	1
2	Livraison Express	1
3	Fret Routier International	2
\.


--
-- Data for Name: sous_traitant; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.sous_traitant (id_sous_traitant, nom_entreprise, contact_personne, numero_telephone, email, adresse) FROM stdin;
1	Globus Trans	Omar Rouchdi	0630405060	omar.r@globustrans.ma	Zone Industrielle, Tanger
2	Rapid Cargo	Nadia El Mansour	0640506070	nadia.m@rapidcargo.ma	Agdal, Rabat
\.


--
-- Data for Name: trajet; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.trajet (id_trajet, distance_km, duree_heures, description, id_destination) FROM stdin;
1	25.50	0.80	Trajet Casablanca-Casablanca (Urbain)	1
2	90.00	1.50	Trajet Casablanca-Rabat (Interurbain)	3
3	240.00	3.00	Trajet Casablanca-Marrakech	4
\.


--
-- Data for Name: type_indispo_chauffeur; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.type_indispo_chauffeur (id_type_indispo_chauffeur, nom_type) FROM stdin;
1	Congé Annuel
2	Maladie
3	Formation
\.


--
-- Data for Name: type_indispo_vehicule; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.type_indispo_vehicule (id_type_indispo_vehicule, nom_type) FROM stdin;
1	Panne Mécanique
2	Entretien Régulier
3	Contrôle Technique
\.


--
-- Data for Name: type_vehicule; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.type_vehicule (id_type_vehicule, nom_type) FROM stdin;
1	Camionnette
2	Camion Froid
3	Porte-conteneur
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.users (id, username, email, password_hash, role) FROM stdin;
1	admin	admin@gmail.com	scrypt:32768:8:1$HjMjU8MiHs5IsC9z$0b957c45329a39ee5aeb50e7a37c842234db2ae8d034baded16596ab99ae20e8aae23288a8231daf73dfb73bf65e29dffe2c2200b92a2898f5f2ad32bcb119a0	ADMIN
\.


--
-- Data for Name: vehicule; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.vehicule (id_vehicule, immatriculation_ve, categorie) FROM stdin;
1	A-12345-01	Camion
2	B-67890-02	Utilitaire
3	C-11223-03	Semi-remorque
\.


--
-- Data for Name: vehicule_externe; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.vehicule_externe (id_vehicule_externe, immatriculation_ve, categorie, description, id_sous_traitant) FROM stdin;
1	GT-45678	Porteur	Camion 10T	1
2	RC-90123	Fourgon	Fourgonnette de livraison	2
\.


--
-- Data for Name: ville; Type: TABLE DATA; Schema: public; Owner: tms_user
--

COPY public.ville (id_ville, code_ville, nom_ville) FROM stdin;
1	CASA	Casablanca
2	RAB	Rabat
3	MRK	Marrakech
4	FES	Fès
5	TANG	Tanger
6	AGAD	Agadir
\.


--
-- Name: affretement_id_affretement_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.affretement_id_affretement_seq', 2, true);


--
-- Name: chauffeur_externe_id_chauffeur_externe_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.chauffeur_externe_id_chauffeur_externe_seq', 2, true);


--
-- Name: chauffeur_id_chauffeur_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.chauffeur_id_chauffeur_seq', 3, true);


--
-- Name: client_final_id_client_final_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.client_final_id_client_final_seq', 3, true);


--
-- Name: client_initial_id_client_initial_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.client_initial_id_client_initial_seq', 2, true);


--
-- Name: date_cv_id_date_cv_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.date_cv_id_date_cv_seq', 1, true);


--
-- Name: date_tr_id_date_tr_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.date_tr_id_date_tr_seq', 1, true);


--
-- Name: destination_id_destination_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.destination_id_destination_seq', 4, true);


--
-- Name: detail_commande_id_detail_commande_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.detail_commande_id_detail_commande_seq', 4, true);


--
-- Name: entete_commande_id_entete_commande_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.entete_commande_id_entete_commande_seq', 5, true);


--
-- Name: feuille_de_route_id_feuille_de_route_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.feuille_de_route_id_feuille_de_route_seq', 2, true);


--
-- Name: indisponibilite_chauffeur_id_indispo_chauffeur_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.indisponibilite_chauffeur_id_indispo_chauffeur_seq', 2, true);


--
-- Name: indisponibilite_vehicule_id_indispo_vehicule_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.indisponibilite_vehicule_id_indispo_vehicule_seq', 2, true);


--
-- Name: mission_id_mission_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.mission_id_mission_seq', 4, true);


--
-- Name: province_id_province_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.province_id_province_seq', 22, true);


--
-- Name: service_client_id_service_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.service_client_id_service_seq', 3, true);


--
-- Name: sous_traitant_id_sous_traitant_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.sous_traitant_id_sous_traitant_seq', 2, true);


--
-- Name: trajet_id_trajet_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.trajet_id_trajet_seq', 3, true);


--
-- Name: type_indispo_chauffeur_id_type_indispo_chauffeur_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.type_indispo_chauffeur_id_type_indispo_chauffeur_seq', 3, true);


--
-- Name: type_indispo_vehicule_id_type_indispo_vehicule_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.type_indispo_vehicule_id_type_indispo_vehicule_seq', 3, true);


--
-- Name: type_vehicule_id_type_vehicule_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.type_vehicule_id_type_vehicule_seq', 3, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: vehicule_externe_id_vehicule_externe_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.vehicule_externe_id_vehicule_externe_seq', 2, true);


--
-- Name: vehicule_id_vehicule_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.vehicule_id_vehicule_seq', 3, true);


--
-- Name: ville_id_ville_seq; Type: SEQUENCE SET; Schema: public; Owner: tms_user
--

SELECT pg_catalog.setval('public.ville_id_ville_seq', 6, true);


--
-- Name: affretement affretement_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.affretement
    ADD CONSTRAINT affretement_pkey PRIMARY KEY (id_affretement);


--
-- Name: chauffeur chauffeur_email_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.chauffeur
    ADD CONSTRAINT chauffeur_email_key UNIQUE (email);


--
-- Name: chauffeur_externe chauffeur_externe_email_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.chauffeur_externe
    ADD CONSTRAINT chauffeur_externe_email_key UNIQUE (email);


--
-- Name: chauffeur_externe chauffeur_externe_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.chauffeur_externe
    ADD CONSTRAINT chauffeur_externe_pkey PRIMARY KEY (id_chauffeur_externe);


--
-- Name: chauffeur chauffeur_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.chauffeur
    ADD CONSTRAINT chauffeur_pkey PRIMARY KEY (id_chauffeur);


--
-- Name: client_final client_final_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.client_final
    ADD CONSTRAINT client_final_pkey PRIMARY KEY (id_client_final);


--
-- Name: client_initial client_initial_email_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.client_initial
    ADD CONSTRAINT client_initial_email_key UNIQUE (email);


--
-- Name: client_initial client_initial_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.client_initial
    ADD CONSTRAINT client_initial_pkey PRIMARY KEY (id_client_initial);


--
-- Name: date_cv date_cv_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.date_cv
    ADD CONSTRAINT date_cv_pkey PRIMARY KEY (id_date_cv);


--
-- Name: date_tr date_tr_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.date_tr
    ADD CONSTRAINT date_tr_pkey PRIMARY KEY (id_date_tr);


--
-- Name: destination destination_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.destination
    ADD CONSTRAINT destination_pkey PRIMARY KEY (id_destination);


--
-- Name: detail_commande detail_commande_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.detail_commande
    ADD CONSTRAINT detail_commande_pkey PRIMARY KEY (id_detail_commande);


--
-- Name: entete_commande entete_commande_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.entete_commande
    ADD CONSTRAINT entete_commande_pkey PRIMARY KEY (id_entete_commande);


--
-- Name: entete_commande entete_commande_reference_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.entete_commande
    ADD CONSTRAINT entete_commande_reference_key UNIQUE (reference);


--
-- Name: feuille_de_route feuille_de_route_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.feuille_de_route
    ADD CONSTRAINT feuille_de_route_pkey PRIMARY KEY (id_feuille_de_route);


--
-- Name: indisponibilite_chauffeur indisponibilite_chauffeur_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.indisponibilite_chauffeur
    ADD CONSTRAINT indisponibilite_chauffeur_pkey PRIMARY KEY (id_indispo_chauffeur);


--
-- Name: indisponibilite_vehicule indisponibilite_vehicule_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.indisponibilite_vehicule
    ADD CONSTRAINT indisponibilite_vehicule_pkey PRIMARY KEY (id_indispo_vehicule);


--
-- Name: mission_detail mission_detail_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.mission_detail
    ADD CONSTRAINT mission_detail_pkey PRIMARY KEY (id_mission, id_detail_commande);


--
-- Name: mission mission_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.mission
    ADD CONSTRAINT mission_pkey PRIMARY KEY (id_mission);


--
-- Name: province province_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.province
    ADD CONSTRAINT province_pkey PRIMARY KEY (id_province);


--
-- Name: service_client service_client_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.service_client
    ADD CONSTRAINT service_client_pkey PRIMARY KEY (id_service);


--
-- Name: sous_traitant sous_traitant_email_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.sous_traitant
    ADD CONSTRAINT sous_traitant_email_key UNIQUE (email);


--
-- Name: sous_traitant sous_traitant_nom_entreprise_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.sous_traitant
    ADD CONSTRAINT sous_traitant_nom_entreprise_key UNIQUE (nom_entreprise);


--
-- Name: sous_traitant sous_traitant_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.sous_traitant
    ADD CONSTRAINT sous_traitant_pkey PRIMARY KEY (id_sous_traitant);


--
-- Name: trajet trajet_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.trajet
    ADD CONSTRAINT trajet_pkey PRIMARY KEY (id_trajet);


--
-- Name: type_indispo_chauffeur type_indispo_chauffeur_nom_type_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.type_indispo_chauffeur
    ADD CONSTRAINT type_indispo_chauffeur_nom_type_key UNIQUE (nom_type);


--
-- Name: type_indispo_chauffeur type_indispo_chauffeur_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.type_indispo_chauffeur
    ADD CONSTRAINT type_indispo_chauffeur_pkey PRIMARY KEY (id_type_indispo_chauffeur);


--
-- Name: type_indispo_vehicule type_indispo_vehicule_nom_type_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.type_indispo_vehicule
    ADD CONSTRAINT type_indispo_vehicule_nom_type_key UNIQUE (nom_type);


--
-- Name: type_indispo_vehicule type_indispo_vehicule_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.type_indispo_vehicule
    ADD CONSTRAINT type_indispo_vehicule_pkey PRIMARY KEY (id_type_indispo_vehicule);


--
-- Name: type_vehicule type_vehicule_nom_type_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.type_vehicule
    ADD CONSTRAINT type_vehicule_nom_type_key UNIQUE (nom_type);


--
-- Name: type_vehicule type_vehicule_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.type_vehicule
    ADD CONSTRAINT type_vehicule_pkey PRIMARY KEY (id_type_vehicule);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vehicule_externe vehicule_externe_immatriculation_ve_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.vehicule_externe
    ADD CONSTRAINT vehicule_externe_immatriculation_ve_key UNIQUE (immatriculation_ve);


--
-- Name: vehicule_externe vehicule_externe_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.vehicule_externe
    ADD CONSTRAINT vehicule_externe_pkey PRIMARY KEY (id_vehicule_externe);


--
-- Name: vehicule vehicule_immatriculation_ve_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.vehicule
    ADD CONSTRAINT vehicule_immatriculation_ve_key UNIQUE (immatriculation_ve);


--
-- Name: vehicule vehicule_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.vehicule
    ADD CONSTRAINT vehicule_pkey PRIMARY KEY (id_vehicule);


--
-- Name: ville ville_code_ville_key; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.ville
    ADD CONSTRAINT ville_code_ville_key UNIQUE (code_ville);


--
-- Name: ville ville_pkey; Type: CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.ville
    ADD CONSTRAINT ville_pkey PRIMARY KEY (id_ville);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: tms_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: tms_user
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: affretement affretement_id_chauffeur_externe_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.affretement
    ADD CONSTRAINT affretement_id_chauffeur_externe_fkey FOREIGN KEY (id_chauffeur_externe) REFERENCES public.chauffeur_externe(id_chauffeur_externe);


--
-- Name: affretement affretement_id_detail_commande_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.affretement
    ADD CONSTRAINT affretement_id_detail_commande_fkey FOREIGN KEY (id_detail_commande) REFERENCES public.detail_commande(id_detail_commande);


--
-- Name: affretement affretement_id_sous_traitant_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.affretement
    ADD CONSTRAINT affretement_id_sous_traitant_fkey FOREIGN KEY (id_sous_traitant) REFERENCES public.sous_traitant(id_sous_traitant);


--
-- Name: affretement affretement_id_vehicule_externe_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.affretement
    ADD CONSTRAINT affretement_id_vehicule_externe_fkey FOREIGN KEY (id_vehicule_externe) REFERENCES public.vehicule_externe(id_vehicule_externe);


--
-- Name: chauffeur_externe chauffeur_externe_id_sous_traitant_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.chauffeur_externe
    ADD CONSTRAINT chauffeur_externe_id_sous_traitant_fkey FOREIGN KEY (id_sous_traitant) REFERENCES public.sous_traitant(id_sous_traitant);


--
-- Name: client_final client_final_id_client_initial_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.client_final
    ADD CONSTRAINT client_final_id_client_initial_fkey FOREIGN KEY (id_client_initial) REFERENCES public.client_initial(id_client_initial);


--
-- Name: date_cv date_cv_id_chauffeur_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.date_cv
    ADD CONSTRAINT date_cv_id_chauffeur_fkey FOREIGN KEY (id_chauffeur) REFERENCES public.chauffeur(id_chauffeur);


--
-- Name: date_tr date_tr_id_vehicule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.date_tr
    ADD CONSTRAINT date_tr_id_vehicule_fkey FOREIGN KEY (id_vehicule) REFERENCES public.vehicule(id_vehicule);


--
-- Name: destination destination_id_province_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.destination
    ADD CONSTRAINT destination_id_province_fkey FOREIGN KEY (id_province) REFERENCES public.province(id_province);


--
-- Name: destination destination_id_ville_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.destination
    ADD CONSTRAINT destination_id_ville_fkey FOREIGN KEY (id_ville) REFERENCES public.ville(id_ville);


--
-- Name: detail_commande detail_commande_id_client_final_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.detail_commande
    ADD CONSTRAINT detail_commande_id_client_final_fkey FOREIGN KEY (id_client_final) REFERENCES public.client_final(id_client_final);


--
-- Name: detail_commande detail_commande_id_destination_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.detail_commande
    ADD CONSTRAINT detail_commande_id_destination_fkey FOREIGN KEY (id_destination) REFERENCES public.destination(id_destination);


--
-- Name: detail_commande detail_commande_id_entete_commande_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.detail_commande
    ADD CONSTRAINT detail_commande_id_entete_commande_fkey FOREIGN KEY (id_entete_commande) REFERENCES public.entete_commande(id_entete_commande);


--
-- Name: detail_commande detail_commande_id_type_vehicule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.detail_commande
    ADD CONSTRAINT detail_commande_id_type_vehicule_fkey FOREIGN KEY (id_type_vehicule) REFERENCES public.type_vehicule(id_type_vehicule);


--
-- Name: entete_commande entete_commande_id_client_initial_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.entete_commande
    ADD CONSTRAINT entete_commande_id_client_initial_fkey FOREIGN KEY (id_client_initial) REFERENCES public.client_initial(id_client_initial);


--
-- Name: entete_commande entete_commande_id_service_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.entete_commande
    ADD CONSTRAINT entete_commande_id_service_fkey FOREIGN KEY (id_service) REFERENCES public.service_client(id_service);


--
-- Name: feuille_de_route feuille_de_route_id_chauffeur_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.feuille_de_route
    ADD CONSTRAINT feuille_de_route_id_chauffeur_fkey FOREIGN KEY (id_chauffeur) REFERENCES public.chauffeur(id_chauffeur);


--
-- Name: feuille_de_route feuille_de_route_id_vehicule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.feuille_de_route
    ADD CONSTRAINT feuille_de_route_id_vehicule_fkey FOREIGN KEY (id_vehicule) REFERENCES public.vehicule(id_vehicule);


--
-- Name: indisponibilite_chauffeur indisponibilite_chauffeur_id_chauffeur_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.indisponibilite_chauffeur
    ADD CONSTRAINT indisponibilite_chauffeur_id_chauffeur_fkey FOREIGN KEY (id_chauffeur) REFERENCES public.chauffeur(id_chauffeur);


--
-- Name: indisponibilite_chauffeur indisponibilite_chauffeur_id_type_indispo_chauffeur_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.indisponibilite_chauffeur
    ADD CONSTRAINT indisponibilite_chauffeur_id_type_indispo_chauffeur_fkey FOREIGN KEY (id_type_indispo_chauffeur) REFERENCES public.type_indispo_chauffeur(id_type_indispo_chauffeur);


--
-- Name: indisponibilite_vehicule indisponibilite_vehicule_id_type_indispo_vehicule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.indisponibilite_vehicule
    ADD CONSTRAINT indisponibilite_vehicule_id_type_indispo_vehicule_fkey FOREIGN KEY (id_type_indispo_vehicule) REFERENCES public.type_indispo_vehicule(id_type_indispo_vehicule);


--
-- Name: indisponibilite_vehicule indisponibilite_vehicule_id_vehicule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.indisponibilite_vehicule
    ADD CONSTRAINT indisponibilite_vehicule_id_vehicule_fkey FOREIGN KEY (id_vehicule) REFERENCES public.vehicule(id_vehicule);


--
-- Name: mission_detail mission_detail_id_detail_commande_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.mission_detail
    ADD CONSTRAINT mission_detail_id_detail_commande_fkey FOREIGN KEY (id_detail_commande) REFERENCES public.detail_commande(id_detail_commande);


--
-- Name: mission_detail mission_detail_id_mission_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.mission_detail
    ADD CONSTRAINT mission_detail_id_mission_fkey FOREIGN KEY (id_mission) REFERENCES public.mission(id_mission);


--
-- Name: mission mission_id_chauffeur_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.mission
    ADD CONSTRAINT mission_id_chauffeur_fkey FOREIGN KEY (id_chauffeur) REFERENCES public.chauffeur(id_chauffeur);


--
-- Name: mission mission_id_destination_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.mission
    ADD CONSTRAINT mission_id_destination_fkey FOREIGN KEY (id_destination) REFERENCES public.destination(id_destination);


--
-- Name: mission mission_id_feuille_de_route_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.mission
    ADD CONSTRAINT mission_id_feuille_de_route_fkey FOREIGN KEY (id_feuille_de_route) REFERENCES public.feuille_de_route(id_feuille_de_route);


--
-- Name: mission mission_id_vehicule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.mission
    ADD CONSTRAINT mission_id_vehicule_fkey FOREIGN KEY (id_vehicule) REFERENCES public.vehicule(id_vehicule);


--
-- Name: province province_id_ville_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.province
    ADD CONSTRAINT province_id_ville_fkey FOREIGN KEY (id_ville) REFERENCES public.ville(id_ville);


--
-- Name: service_client service_client_id_client_initial_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.service_client
    ADD CONSTRAINT service_client_id_client_initial_fkey FOREIGN KEY (id_client_initial) REFERENCES public.client_initial(id_client_initial);


--
-- Name: trajet trajet_id_destination_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.trajet
    ADD CONSTRAINT trajet_id_destination_fkey FOREIGN KEY (id_destination) REFERENCES public.destination(id_destination);


--
-- Name: vehicule_externe vehicule_externe_id_sous_traitant_fkey; Type: FK CONSTRAINT; Schema: public; Owner: tms_user
--

ALTER TABLE ONLY public.vehicule_externe
    ADD CONSTRAINT vehicule_externe_id_sous_traitant_fkey FOREIGN KEY (id_sous_traitant) REFERENCES public.sous_traitant(id_sous_traitant);


--
-- PostgreSQL database dump complete
--

