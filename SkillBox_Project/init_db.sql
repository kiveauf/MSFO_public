CREATE TABLE IF NOT EXISTS public.ticker_info
(
    url text COLLATE pg_catalog."default" NOT NULL,
    name character varying(4) COLLATE pg_catalog."default" NOT NULL,
    pribyl numeric(25,5),
    viruchka numeric(25,5),
    price numeric(25,5),
    amount numeric(25,5),
    measuring_unit integer,
    pe numeric(5,2),
    ps numeric(5,2),
    CONSTRAINT ticker_info_pkey PRIMARY KEY (url)
);

CREATE TABLE IF NOT EXISTS public.ticker_pages
(
    url text COLLATE pg_catalog."default" NOT NULL,
    line text COLLATE pg_catalog."default",
    CONSTRAINT ticker_pages_ticker_pkey PRIMARY KEY (url),
    CONSTRAINT ticker_pages_fkey FOREIGN KEY (url)
        REFERENCES public.ticker_info (url) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);