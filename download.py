import requests
from html.parser import HTMLParser
import datetime as dt
from os.path import exists
from os.path import join
from os import scandir

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
    #asume el primero como el más reciente
    ds_str = parser.dataset[0]
    ds_date = dt.datetime.strptime(ds_str, remoto['catalog_fmt'])
    try:
        new_remoto = ds_date>local['fecha']
        if new_remoto == True:
            remoto['fecha']= ds_date

    except KeyError:
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

