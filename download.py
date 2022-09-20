import requests
from html.parser import HTMLParser
import datetime as dt

#configura parser para filtrar los enlaces a los datos
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
fmt = 'catalog.html?dataset=GOMu0.04/expt_90.1m000/FMRC/runs/GOMu0.04_901m000_FMRC_RUN_%Y-%m-%dT%H:%M:%S%z'
url = 'http://ncss.hycom.org/thredds/catalog/GOMu0.04/expt_90.1m000/FMRC/runs/catalog.html'
#url = 'https://tds.hycom.org/thredds/catalog/GOMu0.04/expt_90.1m000/FMRC/runs/catalog.html'
page = requests.get(url)
if page.status_code != 200:
    print('Error, status:', page.status_code)
    exit()
else:
    print('servidor en línea')
parser = MyHTMLParser()
parser.feed(page.text)
hoy =dt.datetime.now(dt.timezone.utc)
print('fecha actual:', hoy)
hoy = dt.datetime(hoy.year, hoy.month, hoy.day, tzinfo=dt.timezone.utc)
#asume el primero como el más reciente
ds_str = parser.dataset[0]
ds_date = dt.datetime.strptime(ds_str, fmt)
print('ultimo archivo:', ds_str,ds_date)
if ds_date>hoy:
    print('Datos actuales disponibles')
else:
    print('No hay datos actuales')
