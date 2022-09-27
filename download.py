import requests
from html.parser import HTMLParser
import datetime as dt
from os.path import exists
from os.path import join
from os import scandir
from netCDF4 import Dataset
import numpy as np
import os

#configura parser para filtrar los enlaces a los datos
# en un catalogo THREDDS
#etiqueta A
#atributo href
class MyHTMLParser(HTMLParser):
    def __init__(self,):
        HTMLParser.__init__(self,)
        self.dataset = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (atr, val) in attrs:
                if atr =='href':
                    if 'dataset' in val:
                        self.dataset.append(val)

def check_update( local, remoto):
    #obteniendo fecha UTC y truncando a dia
    hoy =dt.datetime.now(dt.timezone.utc)
    print('fecha actual:', hoy)
    hoy = dt.datetime(
            hoy.year,
            hoy.month,
            hoy.day,
            12,
            tzinfo=dt.timezone.utc)
    with scandir(local['path']) as filenames:
        for filename in filenames:
            if filename.is_file():
                try:
                    local_date = dt.datetime.strptime(filename.name, local['name_fmt'])
                except:
                    continue
                try:
                    if local_date<=local['fecha']:
                        new_local = False
                except:
                    new_local = True
                if new_local == True:
                    local['fecha'] = local_date
                    local['nombre'] = filename.name
                    local['day'] = dt.datetime(
                            local_date.year,
                            local_date.month,
                            local_date.day,
                            tzinfo =dt.timezone.utc)
    #Obteniendo página
    page = requests.get( remoto['catalog'])
    if page.status_code != 200:
        #print('Error, status:', page.status_code)
        return None
    parser = MyHTMLParser()
    #Analizando contenido
    parser.feed(page.text)
    #busca el primer elemento en coincidir con el formato
    #asume el primero como el más reciente
    for ds_link in parser.dataset:
        try:
            ds_date = dt.datetime.strptime(ds_link, remoto['catalog_fmt'])
            break
        except:
            pass
    try:
        new_remoto = ds_date>local['fecha']
        if new_remoto == True:
            remoto['fecha']= ds_date

    except KeyError:
        remoto['fecha']= ds_date
        return True
    return new_remoto

def get_req(remoto):
    req = remoto['request']['URL']
    req += remoto['fecha'].strftime(remoto['request']['name_fmt'])
    var_req= remoto['request']['vars']
    page = requests.get(req, params =var_req)
    filename= join(remoto['path'],
            remoto['fecha'].strftime(remoto['name_fmt']))
    with open(filename,'wb') as fp:
        fp.write(page.content)
    print(filename, 'guardado')
    return(filename)

def prep_wrf(filename):
    print('procesando:', filename)
    with  Dataset(filename, 'r', format='NETCDF4_CLASSIC') as ds:
        data_u = ds['U10'][:]
        data_v = ds['V10'][:]
        data_lat = ds['XLAT'][0,:,0]
        data_lon = ds['XLONG'][0,0,:]
        secs = ds['Time'][:]

    time = []
    for s in secs:
        time.append(dt.datetime.fromtimestamp(s, dt.timezone.utc))
    t_units = time[0].strftime("hours since %Y-%m-%d %H:%M:%S UTC")
    hours = []
    for t in time:
        hours.append((t-time[0]).total_seconds()/3600)
    hours = np.array(hours)
    fillValue = 1.267651e+30
    with Dataset(filename, 'w', format='NETCDF3_CLASSIC') as dataset:
        dataset.createDimension('time', hours.shape[0])
        dataset.createDimension('lat', data_lat.shape[0])
        dataset.createDimension('lon', data_lon.shape[0])
        time = dataset.createVariable('time', np.float64, ('time', ))
        lon = dataset.createVariable('lon', np.float32, ('lon', ))
        lat = dataset.createVariable('lat', np.float32, ('lat', ))
        u = dataset.createVariable('u', (np.float32), ('time', 'lat', 'lon'), fill_value=fillValue)
        v = dataset.createVariable('v', (np.float32), ('time', 'lat', 'lon'), fill_value=fillValue)
        dataset.grid_type = 'REGULAR'
        lat.long_name = 'Latitude'
        lat.units = 'degrees_north'
        lat.standard_name = 'latitude'
        lon.long_name = 'Longitude'
        lon.units = 'degrees_east'
        lon.standard_name = 'longitude'
        time.long_name = 'Time'
        time.units = t_units
        time.standard_name = 'time'
        u.long_name = 'Eastward Air Velocity'
        u.standard_name = 'eastward_wind'
        u.units = 'm/s'
        v.long_name = 'Northward Air Velocity'
        v.standard_name = 'northward_wind'
        v.units = 'm/s'
        lat[:] = data_lat
        lon[:] = data_lon
        time[:] = hours
        u[:] = data_u
        v[:] = data_v

def prep_hycom(filename):
    if os.stat(filename).st_size < 1024:
        os.remove(filename)
        print('archivo demadiado pequeño')
        print(filename, 'borrado')
    else:
        print('tamaño de archivo adecuado')
