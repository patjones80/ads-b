-- public.flights definition

-- Drop table
-- DROP TABLE public.flights;

CREATE TABLE public.flights_kpdx (
	now numeric(11, 1) NULL,
	adsb_date date NULL,
	adsb_time time NULL,
	hex bpchar(6) DEFAULT NULL::bpchar NULL,
	message_type text NULL,
	flight bpchar(8) DEFAULT NULL::bpchar NULL,
	alt_baro int4 NULL,
	alt_geom int4 NULL,
	gs numeric NULL,
	ias numeric NULL,
	tas numeric NULL,
	mach numeric NULL,
	track int2 NULL,
	track_rate int2 NULL,
	roll int2 NULL,
	mag_heading int2 NULL,
	true_heading int2 NULL,
	baro_rate int4 NULL,
	geom_rate int4 NULL,
	squawk bpchar(4) DEFAULT NULL::bpchar NULL,
	emergency varchar(4) DEFAULT NULL::character varying NULL,
	category bpchar(2) DEFAULT NULL::bpchar NULL,
	nav_qnh numeric(5, 1) DEFAULT NULL::numeric NULL,
	nav_altitude_mcp int4 NULL,
	nav_altitude_fms int4 NULL,
	nav_heading numeric NULL,
	nav_modes _text NULL,
	lat numeric NULL,
	lon numeric NULL,
	nic int2 NULL,
	rc int4 NULL,
	seen_pos numeric NULL,
	adsb_version int2 NULL,
	nic_baro int2 NULL,
	nac_p int2 NULL,
	sil int2 NULL,
	sil_type varchar NULL,
	gva int2 NULL,
	sda int2 NULL,
	modea bool NULL,
	modec bool NULL,
	mlat _text NULL,
	tisb _text NULL,
	messages int4 NULL,
	seen numeric NULL,
	rssi numeric NULL,
	inserted_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	"version" int4 NULL,
	nac_v int4 NULL,
	"type" varchar NULL,
	CONSTRAINT flights_kpdx_unique UNIQUE (now, hex)
);

CREATE INDEX idx_1_pdx ON public.flights_kpdx USING btree (now);
CREATE INDEX idx_adsb_date_pdx ON public.flights_kpdx USING btree (adsb_date);
CREATE INDEX idx_hex_enhanced_pdx ON public.flights_kpdx USING btree (hex);
CREATE INDEX idx_now_enhanced_pdx ON public.flights_kpdx USING btree (now);

-- public.icao_lookup definition

-- Drop table
-- DROP TABLE public.icao_lookup;

CREATE TABLE public.icao_lookup (
	hex text NOT NULL,
	load_date date NULL,
	reg text NULL,
	manufacturer text NULL,
	"type" text NULL,
	type_icao text NULL,
	"owner" text NULL,
	flag_code text NULL,
	CONSTRAINT icao_lookup_pkey PRIMARY KEY (hex)
);


-- public.icao_not_found definition

-- Drop table
-- DROP TABLE public.icao_not_found;

CREATE TABLE public.icao_not_found (
	hex varchar(6) NOT NULL,
	load_date date NULL,
	CONSTRAINT icao_not_found_pkey PRIMARY KEY (hex)
); 
