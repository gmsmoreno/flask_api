import geopandas as gpd
from sqlalchemy import create_engine
import psycopg2
from geoalchemy2 import Geometry
import fiona
from shapely import wkb
import os
import pandas as pd
from shapely.geometry import MultiPolygon

class aprovIngest:
      def __init__(self, file, gpkgfile):
            self.file = file
            self.gpkgfile = gpkgfile

      def conectDb():         
            user = 'postgres'
            password = 'postgres'
            host = 'localhost'
            port = 5432
            database = 'postgres'

            global engine
            engine = create_engine(
                  url="postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(
                        user, password, host, port, database
                  )
            )
      
      def dataProcessing(file):
            aprovIngest.conectDb()
            fiona.supported_drivers['KML'] = 'rw'
            fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
            fiona.drvsupport.supported_drivers['KML'] = 'rw'
            fiona.os.environ['SHAPE_RESTORE_SHX'] = 'YES'

            if ".kml" in file:
                  f = file
                  df = gpd.GeoDataFrame()
                  # iterate over layers
                  for layer in fiona.listlayers(f):
                        s = gpd.read_file(f, driver='KML', layer=layer)
                        nome = [os.path.splitext(os.path.basename(file))[0]]
                        s['nome_arqui'] = nome[0]
                        df = pd.concat([df, s],  ignore_index=True)

                  gdf = gpd.GeoDataFrame(df, geometry="geometry")

            elif ".kmz" in file:
                  f = file
                  df = gpd.GeoDataFrame()
                  # iterate over layers
                  for layer in fiona.listlayers(f):
                        s = gpd.read_file(f, driver='KMZ', layer=layer)
                        nome = [os.path.splitext(os.path.basename(file))[0]]
                        s['nome_arqui'] = nome[0]
                        df = pd.concat([df, s],  ignore_index=True)

                  gdf = gpd.GeoDataFrame(df, geometry="geometry")

            else:
                  gdf = gpd.read_file(file)
                  nome = [os.path.splitext(os.path.basename(file))[0]]
                  gdf['nome_arqui'] = nome[0]


            gdf.geometry = gdf.buffer(0)

            gdf = gdf.dissolve(by = ['nome_arqui']).reset_index()

            if file and gdf.geometry.geom_type[0] == 'Polygon':
                  gdf.geometry = gdf.geometry.apply(lambda x: MultiPolygon([x]))

            _drop_z = lambda geom: wkb.loads(wkb.dumps(geom, output_dimension=2))

            gdf.geometry = gdf.geometry.transform(_drop_z)

            gdf.geometry = gdf.geometry.to_crs({'init': 'epsg:4326'})

            gdf['area'] = gdf['geometry'].to_crs({'init': 'epsg:6933'})\
                  .map(lambda p: p.area / 10000)
          
            return gdf[['nome_arqui', 'area', 'geometry']]
          
      def ingestDb(file):
          gdf = aprovIngest.dataProcessing(file)

          gdf.to_postgis("aprovados_geom", 
               engine,
               #schema='pmr_aprov',
               if_exists='append', 
               index=False)
      
      def exportDb(gpkgfile):
           aprovIngest.conectDb()
           sql = '''SELECT * FROM VW_APROVADOS;'''
           gdf = gpd.read_postgis(sql, engine, index_col=None)

           gdf.to_file(gpkgfile)