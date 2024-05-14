from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
#import magic
import urllib.request
from aprovDb import aprovIngest
from datetime import date
from datetime import datetime

app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@10.119.200.2/postgres'

db=SQLAlchemy(app)

app.config["SECRET_KEY"] = 'postgres'

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

EXT_FOLDER = os.path.join(os.getcwd(), 'arquivos')

ALLOWED_EXTENSIONS = set(['shp', 'shx', 'prj', 'dbf', 'cpg', 'gpkg', 'kml', 'kmz'])

SHP_EXTENSIONS = set(['shp', 'shx', 'prj', 'dbf', 'cpg'])

SHP_EXT = set(['shp'])

GPKG_EXT = set(['gpkg'])

KML_EXT = set(['kml'])

KMZ_EXT = set(['kmz'])

def allowed_file(filename):
      return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def shp_file(filename):
      return '.' in filename and filename.rsplit('.', 1)[1].lower() in SHP_EXTENSIONS

def shp_ext(filename):
      return '.' in filename and filename.rsplit('.', 1)[1].lower() in SHP_EXT

def gpkg_ext(filename):
      return '.' in filename and filename.rsplit('.', 1)[1].lower() in GPKG_EXT

def kml_ext(filename):
      return '.' in filename and filename.rsplit('.', 1)[1].lower() in KML_EXT

def kmz_ext(filename):
      return '.' in filename and filename.rsplit('.', 1)[1].lower() in KMZ_EXT

class aprovadosProdutores(db.Model):
      __tablename__='aprovados'
      id=db.Column(db.Integer, primary_key=True)
      fase=db.Column(db.String(40))
      cooperativa=db.Column(db.String(40))
      cod_cooper=db.Column(db.String(40))
      proprietario=db.Column(db.String(40))
      area_aprov=db.Column(db.String(150))
      dt_envio=db.Column(db.String(40))
      dt_analise=db.Column(db.String(40))
      nome_arqui=db.Column(db.String(150))
      #nome_ext = db.Column(db.String(150))


@app.route('/')
def index():
      return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
      input_files = request.files.getlist('files[]')
      fase = request.form['fase']
      cooperativa = request.form['cooperativa']
      cod_cooper = request.form['cod_cooper']
      proprietario = request.form['proprietario']
      area_aprov = request.form['area_aprov']
      dt_analise = request.form['dt_analise']
      dt_analise = datetime.strptime(dt_analise, '%Y-%m-%d').strftime('%m/%d/%Y')
      dt_envio = request.form['dt_envio']
      dt_envio = datetime.strptime(dt_envio, '%Y-%m-%d').strftime('%m/%d/%Y')
      nome_arqui = request.form['nome_arqui']
      data_atual = date.today()
      data_string = data_atual.strftime('%Y%m%d')
      geoname = f'4_63_{data_string}.shp'
      expPath = os.path.join(EXT_FOLDER, geoname)

      if input_files:
            for file in input_files:
                  if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        pathname = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(pathname)
                        newFile = aprovadosProdutores(
                                          fase=fase, 
                                          cooperativa=cooperativa,
                                          cod_cooper=cod_cooper, 
                                          proprietario=proprietario,
                                          area_aprov=area_aprov,
                                          dt_analise=dt_analise,
                                          dt_envio=dt_envio,
                                          nome_arqui=nome_arqui
                                          )
                        db.session.add(newFile)
                        db.session.commit()
            # Processamento e carregamento de arquivos espaciais no BD
                        if file and shp_ext(file.filename):
                              filename = secure_filename(file.filename)
                              savenameshp = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                              aprovIngest.ingestDb(savenameshp)
                        elif file and gpkg_ext(file.filename):
                              filename = secure_filename(file.filename)
                              savenameshp = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                              aprovIngest.ingestDb(savenameshp)
                        elif file and kml_ext(file.filename):
                              filename = secure_filename(file.filename)
                              savenameshp = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                              aprovIngest.ingestDb(savenameshp)
                        elif file and kmz_ext(file.filename):
                              filename = secure_filename(file.filename)
                              savenameshp = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                              aprovIngest.ingestDb(savenameshp)
            
                        flash('File successfully uploaded ' + file.filename + ' !')

            aprovIngest.exportDb(expPath)

      else:
            flash('Invalid Upload only shp, gpkg, kml and kmz')

      return redirect('/')


if __name__== '__main__':
      app.run(debug=False)