from download import check_update
from download import get_req
#url = 'https://tds.hycom.org/thredds/catalog/GOMu0.04/expt_90.1m000/FMRC/runs/catalog.html'
#creando dataset local
local = {}
local['path'] = "data"
local['name_fmt'] = "hycom_%Y-%m-%dT%H%z.nc"
remoto = {}
remoto['path'] = local['path']
remoto['name_fmt'] = local['name_fmt']
remoto['catalog']= 'http://ncss.hycom.org/thredds/catalog/GOMu0.04/expt_90.1m000/FMRC/runs/catalog.html'
remoto['catalog_fmt'] = 'catalog.html?dataset=GOMu0.04/expt_90.1m000/FMRC/runs/GOMu0.04_901m000_FMRC_RUN_%Y-%m-%dT%H:%M:%S%z'
request = {}
request['URL']= 'https://ncss.hycom.org/thredds/ncss/GOMu0.04/expt_90.1m000/FMRC/runs/'
request['name_fmt'] = 'GOMu0.04_901m000_FMRC_RUN_%Y-%m-%dT%H:%M:%SZ?'
pars = {}
pars['var']= 'water_u,water_v'
pars['horizStride']= '1'
#pars['temporal']='all'
pars['timeStride']= '1'
pars['vertCoord']= '0'
pars['accept']= 'netcdf'
request['vars']= pars
remoto['request']= request
print('*'*40)
ans = check_update(local, remoto)
if ans == True:
    get_req(remoto)
elif ans == None:
    print('No se pudo obtener catálogo')
else:
    print('No hay actualizaciones')
