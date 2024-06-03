from flask import Flask, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS #pip install -U flask-cors
from datetime import timedelta

import psycopg2
import psycopg2.extras

app = Flask(__name__)

app.config['SECRET_KEY'] = 'gabrielcoders'
  
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=10)
CORS(app) 

DB_HOST = "localhost"
DB_NAME = "sampledb"
DB_USER = "postgres"
DB_PASS = "postgres"

#conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST) 

@app.route('/')
def home():
    passhash = generate_password_hash('gabrielcoders')
    print(passhash)
    if 'username' in session:
        username = session['username']
        return jsonify({'message' : 'Você já está logado', 'username' : username})
    else:
        resp = jsonify({'message' : 'Não autorizado'})
        resp.status_code = 401
        return resp

@app.route('/login', methods=['POST'])
def login():
    _json = request.json
    _username = _json['username']
    _password = _json['password']
    print(_password)
    # validate the received values
    if _username and _password:
        #check user exists
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)            
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
          
        sql = "SELECT * FROM useraccount WHERE username=%s"
        sql_where = (_username,)
          
        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        username = row['username']
        password = row['password']
        if row:
            if check_password_hash(password, _password):
                session['username'] = username
                cursor.close()
                return jsonify({'message' : 'Você foi logado com sucesso!'})
            else:
                resp = jsonify({'message' : 'Bad Request - senha inválida'})
                resp.status_code = 400
                return resp
    else:
        resp = jsonify({'message' : 'Bad Request - credencial inválida'})
        resp.status_code = 400
        return resp

@app.route('/query')
def get_car():
    if 'username' in session:
        car = request.args.get('car')
        if car:
            try:
                conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute('''drop view if exists car_base CASCADE; 
                                Create or replace view car_base as
                                select car.cod_imovel as car, car.ind_status as status,
                                car.municipio, car.cod_estado as uf,
                                (st_area(st_transform(car.geom, 55555)) / 10000)::text as area, 
                                car.geom from car.area_imovel_df car
                                where car.cod_imovel ilike %s''', (car,))

                cursor.execute('''drop view if exists car_prodes;
                                create or replace view car_prodes as
                                select a.car, a.area, case when a.year is null then 'não houve detecção de desmatamento'
                                when a.year is not null then 'houve detecção de desmatamento' end as desmatamento
                                from
                                (
                                select car.car, area, userr.year, 
                                st_area(st_transform(st_buffer(st_intersection(car.geom, userr.geom), 0), 55555)) / 10000 as desmat,
                                car.geom 
                                from car_base car 
                                left join esg.prodes userr
                                on st_intersects(car.geom, userr.geom)
                                ) a;''')

                cursor.execute('''drop view if exists car_ti;
                                create or replace view car_ti as
                                select a.car, a.area, case when a.desmat is null then 'não há terra indígena sobreposta à fazenda'
                                when a.desmat is not null then concat('TERRA INDÍGENA ', a.terrai_nom) end as terra_indigena
                                from
                                (
                                select car.car, area, userr.terrai_nom,
                                st_area(st_transform(st_buffer(st_intersection(car.geom, userr.geom), 0), 55555)) / 10000 as desmat,
                                car.geom 
                                from car_base car 
                                left join esg.tis_poligonais userr
                                on st_intersects(car.geom, userr.geom)
                                ) a;''')
                cursor.execute('''drop view if exists car_tq;
                                create or replace view car_tq as
                                select a.car, a.area, case when a.desmat is null then 'não há área quilombola sobreposta à fazenda'
                                when a.desmat is not null then concat('ÁREA QUILOMBOLA ', a.nm_comunid) end as areas_quilombolas
                                from
                                (
                                select car.car, area, userr.nm_comunid,
                                st_area(st_transform(st_buffer(st_intersection(car.geom, userr.geom), 0), 55555)) / 10000 as desmat,
                                car.geom 
                                from car_base car 
                                left join esg.tq userr
                                on st_intersects(car.geom, userr.geom)
                                ) a;''')
                cursor.execute('''drop view if exists car_uc;
                                create or replace view car_uc as
                                select a.car, a.area, case when a.desmat is null then 'não há unidade de conservação sobreposta à fazenda'
                                when a.desmat is not null then concat('UNIDADE DE CONSERVAÇÃO ', a.nomeuc) end as uc
                                from
                                (
                                select car.car, area, userr.nomeuc,
                                st_area(st_transform(st_buffer(st_intersection(car.geom, userr.geom), 0), 55555)) / 10000 as desmat,
                                car.geom 
                                from car_base car 
                                left join esg.uc userr
                                on st_intersects(car.geom, userr.geom)
                                ) a;''')

                cursor.execute('''drop view if exists car_assentamento;
                                create or replace view car_assentamento as
                                select a.car, a.area, case when a.desmat is null then 'não há assentamento sobreposto à fazenda'
                                when a.desmat is not null then concat('PROJETO ', a.nome_proje) end as assentamento
                                from
                                (
                                select car.car, area, userr.nome_proje,
                                st_area(st_transform(st_buffer(st_intersection(car.geom, userr.geom), 0), 55555)) / 10000 as desmat,
                                car.geom 
                                from car_base car 
                                left join esg.assentamento userr
                                on st_intersects(car.geom, userr.geom)
                                ) a;''')
                cursor.execute('''drop view if exists car_embargos;
                                create or replace view car_embargos as
                                select a.car, a.area, case when a.desmat is null then 'não há embargo sobreposto à fazenda'
                                when a.desmat is not null then 'Há embargo sobreposto à fazenda' end as embargo
                                from
                                (
                                select car.car, area,
                                st_area(st_transform(st_buffer(st_intersection(car.geom, userr.geom), 0), 55555)) / 10000 as desmat,
                                car.geom 
                                from car_base car 
                                left join esg.embargos_ibama userr
                                on st_intersects(car.geom, userr.geom)
                                ) a;''')

                cursor.execute('''select base.car, base.status, base.area, 
                                prodes.desmatamento,
                                uc.uc,
                                emb.embargo,
                                ti.terra_indigena,
                                ass.assentamento,
                                tq.areas_quilombolas,
                                base.municipio,
                                base.uf
                                from car_base base
                                join car_embargos emb 
                                on base.car = emb.car
                                join car_ti ti 
                                on base.car = ti.car
                                join car_prodes prodes 
                                on base.car = prodes.car
                                join car_uc uc 
                                on base.car = uc.car
                                join car_assentamento ass 
                                on base.car = ass.car
                                join car_tq tq
                                on base.car = tq.car;''')
                row = cursor.fetchone()
                if row:
                    resp = jsonify(row)
                    resp.status_code = 200
                    return resp
                else:
                    resp = jsonify({'message': 'CAR not found'})
                    resp.status_code = 404
                    return resp
            except Exception as e:
                print(e)
                resp = jsonify({'message': 'Internal Server Error'})
                resp.status_code = 500
                return resp
            finally:
                cursor.close() 
                conn.close()
        else:
            resp = jsonify({'message': 'CAR parameter not provided'})
            resp.status_code = 400
            return resp
    else: 
        resp = jsonify({'message': 'Unauthorized - Please login first'})
        resp.status_code = 401
        return resp

@app.route('/logout')
def logout():
    if 'username' in session:
        #session.clear()
        session.pop('username', None)
    return jsonify({'message' : 'Você deslogou da conta!'})
 
if __name__ == "__main__":
    app.run()