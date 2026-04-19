--
-- PostgreSQL database dump
--

\restrict W7Gk8lWVaQ2XwFfB022ySIxB7UECY4ibUbK7Xg8FN5ixbVeZpdrQvlqrwxzoGyR

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

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

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS fk_users_department;
ALTER TABLE IF EXISTS ONLY public.departments DROP CONSTRAINT IF EXISTS departments_parent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_correo_electronico_key;
ALTER TABLE IF EXISTS ONLY public.departments DROP CONSTRAINT IF EXISTS departments_pkey;
ALTER TABLE IF EXISTS ONLY public.departments DROP CONSTRAINT IF EXISTS departments_organization_id_key;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.departments;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: departments; Type: TABLE; Schema: public; Owner: flor
--

CREATE TABLE public.departments (
    id character varying(100) NOT NULL,
    name text NOT NULL,
    type character varying(50),
    aliases text[],
    scope text,
    parent_id character varying(100),
    contact jsonb DEFAULT '{}'::jsonb,
    organization_id integer
);


ALTER TABLE public.departments OWNER TO flor;

--
-- Name: users; Type: TABLE; Schema: public; Owner: flor
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nombre text NOT NULL,
    correo_electronico text NOT NULL,
    password_hash text NOT NULL,
    organization_id integer DEFAULT 1 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO flor;

--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: flor
--

COPY public.departments (id, name, type, aliases, scope, parent_id, contact, organization_id) FROM stdin;
despacho_alcalde	Despacho del Alcalde	SECRETARIA	{alcalde,"despacho del alcalde","oficina del alcalde"}	Dirección superior de la administración municipal y representación del municipio.	\N	{}	2
secretaria_privada	Secretaría Privada	SECRETARIA	{privada,"secretaria privada"}	Apoyo directo al Despacho del Alcalde y coordinación de la agenda del alcalde.	\N	{}	3
vicealcaldia_gobernabilidad_seguridad	Vicealcaldía de Gobernabilidad y Seguridad	SECRETARIA	{gobernabilidad,seguridad,"vicealcaldia seguridad"}	Coordinación de políticas de gobierno, seguridad y convivencia ciudadana.	\N	{}	4
vicealcaldia_salud_inclusion_familia	Vicealcaldía de Salud, Inclusión y Familia	SECRETARIA	{salud,inclusion,familia}	Coordinación de políticas sociales, salud pública, familia e inclusión.	\N	{}	6
vicealcaldia_habitat_movilidad_infraestructura_sostenibilidad	Vicealcaldía de Hábitat, Movilidad, Infraestructura y Sostenibilidad	SECRETARIA	{habitat,movilidad,infraestructura,sostenibilidad}	Coordinación del desarrollo físico, ambiental y de movilidad de la ciudad.	\N	{}	5
vicealcaldia_educacion_cultura_participacion_recreacion_deporte	Vicealcaldía de Educación, Cultura, Participación, Recreación y Deporte	SECRETARIA	{educacion,cultura,"participacion ciudadana",recreacion,deporte}	Coordinación de educación, cultura, participación ciudadana y deporte.	\N	{}	7
vicealcaldia_gestion_territorial	Vicealcaldía de Gestión Territorial	SECRETARIA	{"gestion territorial",territorial}	Planeación y ordenamiento del territorio municipal.	\N	{}	8
vicealcaldia_creacion_desarrollo_economico	Vicealcaldía de Creación y Desarrollo Económico	SECRETARIA	{creacion,"desarrollo economico","vicealcaldia economica"}	Coordinación de políticas de desarrollo económico y fomento empresarial.	\N	{}	9
secretaria_gobierno	Secretaría de Gobierno y Gestión del Gabinete	SECRETARIA	{gobierno,gabinete,"secretaria de gobierno"}	Coordinación política y relaciones con el Concejo; espacio público; orden.	\N	{}	10
secretaria_seguridad_convivencia	Secretaría de Seguridad y Convivencia	SECRETARIA	{"seguridad ciudadana",convivencia,"policia municipal"}	Políticas de seguridad urbana, convivencia y articulación con Policía Nacional.	\N	{}	11
secretaria_hacienda	Secretaría de Hacienda	SECRETARIA	{hacienda,impuestos,predial,"industria y comercio",tesoreria}	Gestión fiscal, tributaria y financiera del municipio.	\N	{}	12
secretaria_educacion	Secretaría de Educación	SECRETARIA	{"educacion publica",colegios,"instituciones educativas"}	Administración de la educación preescolar, básica y media en el municipio.	\N	{}	13
secretaria_salud	Secretaría de Salud	SECRETARIA	{"salud publica",hospitales,"regimen subsidiado","sisben salud"}	Rectoría de la salud pública municipal y aseguramiento en salud.	\N	{}	14
secretaria_inclusion_social_familia_derechos_humanos	Secretaría de Inclusión Social, Familia y Derechos Humanos	SECRETARIA	{"inclusion social","derechos humanos",familia,"poblacion vulnerable"}	Atención a poblaciones vulnerables, familia y protección de derechos humanos.	\N	{}	15
secretaria_las_mujeres	Secretaría de las Mujeres	SECRETARIA	{mujeres,"equidad de genero","violencia de genero"}	Políticas de equidad de género y protección frente a violencias contra la mujer.	\N	{}	16
secretaria_juventud	Secretaría de la Juventud	SECRETARIA	{juventud,jovenes}	Políticas públicas de juventud y programas para la población joven.	\N	{}	17
secretaria_cultura_ciudadana	Secretaría de Cultura Ciudadana	SECRETARIA	{cultura,bibliotecas,"casas de la cultura"}	Promoción de cultura, arte, patrimonio, lectura y convivencia cultural.	\N	{}	18
secretaria_participacion_ciudadana	Secretaría de Participación Ciudadana	SECRETARIA	{participacion,jac,"juntas de accion comunal","presupuesto participativo"}	Fomento de la participación ciudadana, JAC y presupuesto participativo.	\N	{}	19
secretaria_infraestructura_fisica	Secretaría de Infraestructura Física	SECRETARIA	{infraestructura,"obras publicas",vias,andenes}	Construcción y mantenimiento de infraestructura pública y vial.	\N	{}	20
secretaria_movilidad	Secretaría de Movilidad	SECRETARIA	{movilidad,transito,"licencias de conduccion",comparendos,semaforos}	Regulación del tránsito, transporte público y movilidad urbana.	\N	{}	21
secretaria_medio_ambiente	Secretaría de Medio Ambiente	SECRETARIA	{"medio ambiente",ambiental,arboles,fauna}	Gestión ambiental, fauna, flora urbana y calidad del aire.	\N	{}	22
secretaria_gestion_territorio	Secretaría de Gestión y Control Territorial	SECRETARIA	{"control territorial","licencias de construccion",urbanismo}	Control urbanístico, licencias de construcción y uso del suelo.	\N	{}	23
secretaria_desarrollo_economico	Secretaría de Desarrollo Económico	SECRETARIA	{"desarrollo economico",emprendimiento,empleo,empresas}	Fomento del desarrollo económico, empleo, emprendimiento y competitividad.	\N	{}	1
secretaria_gestion_humana_servicio_ciudadania	Secretaría de Gestión Humana y Servicio a la Ciudadanía	SECRETARIA	{"gestion humana","servicio a la ciudadania","atencion al ciudadano",pqrsd}	Gestión del talento humano municipal y atención/PQRSD a la ciudadanía.	\N	{}	24
secretaria_comunicaciones	Secretaría de Comunicaciones	SECRETARIA	{comunicaciones,prensa}	Comunicación pública institucional y relaciones con medios.	\N	{}	25
secretaria_suministros_servicios	Secretaría de Suministros y Servicios	SECRETARIA	{suministros,contratacion,"servicios administrativos"}	Adquisición de bienes y servicios y gestión logística del municipio.	\N	{}	26
desarrollo_economico__creacion_fortalecimiento_empresarial	Subsecretaría de Creación y Fortalecimiento Empresarial	SUBSECRETARIA	{"creacion empresarial","fortalecimiento empresarial",emprendimiento}	Apoyo a la creación y fortalecimiento de empresas y emprendedores.	secretaria_desarrollo_economico	{}	27
desarrollo_economico__banco_distrital	Banco Distrital de las Oportunidades	SUBSECRETARIA	{"banco distrital","banco de las oportunidades","credito distrital"}	Acceso a microcrédito y servicios financieros para emprendedores.	secretaria_desarrollo_economico	{}	28
desarrollo_economico__turismo	Subsecretaría de Turismo	SUBSECRETARIA	{turismo}	Promoción turística y regulación del sector turismo en Medellín.	secretaria_desarrollo_economico	{}	30
desarrollo_economico__productividad_competitividad	Subsecretaría de Productividad, Competitividad y Relaciones Internacionales	SUBSECRETARIA	{productividad,competitividad,"relaciones internacionales"}	Promoción de productividad, competitividad y cooperación internacional.	secretaria_desarrollo_economico	{}	29
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: flor
--

COPY public.users (id, nombre, correo_electronico, password_hash, organization_id, created_at) FROM stdin;
3fc87bd5-70a8-4291-b881-c8bdfdad3f20	Demo Alcaldía	demo@flor.local	$2b$12$uB57uJngOLKTLkmYvrV8u.He6y1FewjsWbpY4yZEpvLVU.KSd9qoC	1	2026-04-19 04:17:29.544827+00
30aa2bc8-3362-4859-832c-dc81c3bf39fe	Administrador Flor	admin@flor.com	$2b$12$Rws1rZw2bnwxGE05pxjWG.4zA5vlPp0iGWY/8y0aGqWsSucvdGxqm	1	2026-04-19 10:58:24.209752+00
85ddc8c9-def9-488b-841f-5da75a4c69d8	Funcionario 1 – Desarrollo Económico	funcionario1.desarrolloeconomico@medellin.gov.co	$2b$12$8y3nloPYptpy.oZCguskou9CXlnsBSG.PetF.tGvOml1kyMS/E8wW	1	2026-04-19 12:48:29.249973+00
106941e8-bad3-41af-8901-13a30f31b66f	Funcionario 2 – Desarrollo Económico	funcionario2.desarrolloeconomico@medellin.gov.co	$2b$12$Vq2OC3bTX02CFFDnusI8ie0Yeua5GqXuYDGRIseeuXmuJqW.ShDKe	1	2026-04-19 12:48:29.249973+00
213cc1e7-3709-4cb9-bfc4-28cabd956b92	Funcionario 3 – Desarrollo Económico	funcionario3.desarrolloeconomico@medellin.gov.co	$2b$12$/GN5kX1d8gx4TYu21R1xDuSqzIOqpLxZby2XjJJ.gSqmp/K1oFfZW	1	2026-04-19 12:48:29.249973+00
b9edae9f-84f5-41de-9fc9-d38c886c8dc4	Funcionario 4 – Desarrollo Económico	funcionario4.desarrolloeconomico@medellin.gov.co	$2b$12$JAV1ERwt3WICYCLIvffMXO7b72Jyazp2ubwsQzuiSAx8ze5N/rM4e	1	2026-04-19 12:48:29.249973+00
a71ac1ca-01fa-4c7f-9898-035a22ee1931	Funcionario 5 – Desarrollo Económico	funcionario5.desarrolloeconomico@medellin.gov.co	$2b$12$dQQBO56lBG81mrhkrbUZneqiRnjgGLcfoMKBBMj4STYpB5hXhZArm	1	2026-04-19 12:48:29.249973+00
ca66453d-423b-4eb4-b057-cb855383163a	Funcionario – MedioAmbiente	funcionario.medioambiente@medellin.gov.co	$2b$12$n7bNcjZx6lkpRbX5TVIgeOhQW3RE/QxSZsDYbF1vcdffgjjBwHOe2	22	2026-04-19 12:48:29.249973+00
43bcbc53-e8d3-4a66-a93d-c79dbaf2440b	Funcionario – Habitat	funcionario.habitat@medellin.gov.co	$2b$12$XlsXvMjOtPdEOfITXbqXnuhaizECI1aMhaN5tSwpA2WxUd7O6VVtO	5	2026-04-19 12:48:29.249973+00
3c238768-9321-4d5e-ad05-efef90d36a43	Funcionario – Alcalde	funcionario.alcalde@medellin.gov.co	$2b$12$AjxWMPGaFii/eLoExQMU5ezyA7DPCz2Y1X.LVTFZOv4zD8ggxjnDi	2	2026-04-19 12:48:29.249973+00
fa774e86-5e96-4f6e-a047-4b704fab0bf5	Funcionario – Comunicaciones	funcionario.comunicaciones@medellin.gov.co	$2b$12$klG1aUyYvF8KJtNyAcHXPezv0BID6Re1TWWLLh951S9QJv6jfvdjC	25	2026-04-19 12:48:29.249973+00
515fc057-1d3c-4de9-bf31-e61aadc6ad34	Funcionario – Gobierno	funcionario.gobierno@medellin.gov.co	$2b$12$Y3AB2llcB9sHDfD01Q4HhuEKg4zZsHEOZAEQb1u1JV32rqJfnUQnC	10	2026-04-19 12:48:29.249973+00
47d0646f-4375-4713-8cb0-e6200659a66d	Funcionario – ViceEconomica	funcionario.viceeconomica@medellin.gov.co	$2b$12$wwDOSfYAuzEmXVvr8ZRXquH7FZly4NgD3Ac31AjrjH.Xf58gEJwNW	9	2026-04-19 12:48:29.249973+00
ce4d1733-db73-41e9-8048-531143b5203d	Funcionario – Emprendimiento	funcionario.emprendimiento@medellin.gov.co	$2b$12$CzZmFtU/jvX/z8ibKnSUyeJoTVuLead13nwjQLIqNslfQnFRacB7O	27	2026-04-19 12:48:29.249973+00
07fcc9b1-cc3e-43be-b859-a2638a7a2a32	Funcionario – SaludInclusion	funcionario.saludinclusion@medellin.gov.co	$2b$12$LbEJwUYL14EO4mRqmkqF6.XhKoiXAs82z7j5qreK.9cwfUyNRkAFa	6	2026-04-19 12:48:29.249973+00
fcfc4591-3f5a-42e9-9408-857e999b01ec	Funcionario – Productividad	funcionario.productividad@medellin.gov.co	$2b$12$yfO/T1eIfyi9eriNE/zA1OZyB3t6QQ4NMAftd4gbvOYLsWrBwZDi6	29	2026-04-19 12:48:29.249973+00
ff8ed8a3-cecc-4fbb-bf84-fe6cc2cc5c99	Funcionario – Participacion	funcionario.participacion@medellin.gov.co	$2b$12$U9hqPtGP.nxt4hGroMdZIuXqJGL0tmxsBxYXfl336KugrTN0p3x9y	19	2026-04-19 12:48:29.249973+00
\.


--
-- Name: departments departments_organization_id_key; Type: CONSTRAINT; Schema: public; Owner: flor
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_organization_id_key UNIQUE (organization_id);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: flor
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: users users_correo_electronico_key; Type: CONSTRAINT; Schema: public; Owner: flor
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_correo_electronico_key UNIQUE (correo_electronico);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: flor
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: departments departments_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flor
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.departments(id);


--
-- Name: users fk_users_department; Type: FK CONSTRAINT; Schema: public; Owner: flor
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_department FOREIGN KEY (organization_id) REFERENCES public.departments(organization_id);


--
-- PostgreSQL database dump complete
--

\unrestrict W7Gk8lWVaQ2XwFfB022ySIxB7UECY4ibUbK7Xg8FN5ixbVeZpdrQvlqrwxzoGyR

