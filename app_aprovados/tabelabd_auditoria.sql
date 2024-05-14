SELECT * FROM aprovados;

drop table if exists aprovados CASCADE;
CREATE TABLE aprovados (
	id serial PRIMARY KEY,
	fase VARCHAR ( 40 ) NOT NULL,
	cooperativa VARCHAR ( 40 ) NOT NULL,
	cod_cooper VARCHAR ( 10 ) NOT NULL,
	proprietario VARCHAR ( 40 ) NOT null,
	area_aprov VARCHAR ( 150 ) null,
	dt_envio VARCHAR ( 40 ) null,
	dt_analise VARCHAR ( 40 ) null,
	nome_arqui VARCHAR (150) null--,
	--nome_ext VARCHAR ( 150 ) NULL
);

alter sequence aprovados_id_seq1 restart with 24057;

alter sequence aprovados_geom_id_seq restart with 24057;

truncate aprovados;

truncate aprovados_geom;

alter table aprovados add column if not exists dt_inclus_geo text;

alter table aprovados  
alter column dt_inclus_geo SET DEFAULT to_char(current_date, 'MM/DD/YYYY');

drop view if exists vw_aprovados;
create or replace view vw_aprovados as
SELECT aprov.id, aprov.fase, aprov.cooperativa, aprov.cod_cooper,
aprov.proprietario, aprov.area_aprov, aprov.dt_envio, aprov.dt_analise, aprov.dt_inclus_geo, aprov.nome_arqui as nome,
aprov_geom.nome_arqui, aprov_geom.area, munic.nome as municipio, uf.sigla as uf, aprov_geom.geometry as geom
FROM aprovados_geom_test aprov_geom, aprovados_test aprov, ibge.br_municipio munic, ibge.br_estados uf
where aprov_geom.id = aprov.id
and st_intersects(st_centroid(aprov_geom.geometry), st_transform(munic.geom, 4326))
and st_intersects(st_centroid(aprov_geom.geometry), st_transform(uf.geom, 4326));

SELECT nextval('aprovados_id_seq1');

SELECT nextval('aprovados_geom_id_seq');