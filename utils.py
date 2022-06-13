from datetime import datetime, timedelta
from glob import glob

import pandas as pd
import pyproj
import rioxarray
from shapely.geometry import mapping


def define_modis_date(data, link):
    
    # define date of the data
    index_date = link.find('A2') # date starts with A2 tag
    year = link[index_date+1:][:4]
    day = link[index_date+1:][4:7]
    
    # full date --> year + day
    date = datetime(int(year), 1, 1) + timedelta(days = int(day)-1)
    
    # assign date as a coordinate to dataset
    data = data.assign_coords({'time': date})
    
    return data

def find_modis_proj(link):
    
    # crs of the data
    return rioxarray.open_rasterio(link, engine='netcdf4').rio.crs


def define_dmsp_date(data, link):
    
    # find F tag after which the date is located on the link
    F_tag = link.find('F')
    year = link[F_tag+3:F_tag+7]
    
    # assign time as a coord
    data = data.assign_coords({'time': int(year)})
    return data


def define_corine_date(data, link):
    
    # find F tag after which the date is located on the link
    F_tag = link.find('CLC')
    year = link[F_tag+3:F_tag+7]
    
    # assign time as a coord
    data = data.assign_coords({'time': int(year)})
    return data


def find_wrf_proj(data):
    
    proj = pyproj.Proj(proj='lcc', # projection type: Lambert Conformal Conic
                   lat_1=data.attrs['TRUELAT1'],
                   lat_2=data.attrs['TRUELAT2'], # Cone intersects with the sphere
                   lat_0=data.attrs['MOAD_CEN_LAT'],
                   lon_0=data.attrs['STAND_LON'], # Center point
                   a=6370000,
                   b=6370000).crs # The Earth is a perfect sphere
    
    return proj


def create_encode_and_decode():
    
    t_alphabet = 'ÇçĞğİıÖöŞşÜüÂâ'
    t_encodes = {}
    t_decodes = {}
    
    for t in t_alphabet:
        
        match = {'Ç':'C',
                 'ç':'c',
                 'Ğ':'G',
                 'ğ':'g',
                 'İ':'I',
                 'ı':'i',
                 'Ö':'O',
                 'ö':'o',
                 'Ş':'S',
                 'ş':'s',
                 'Ü':'U',
                 'ü':'u',
                 'Â':'A',
                 'â':'a',}
        
        # encode
        t_encodes[t] = t.encode()
        # decode
        t_decodes[t_encodes[t]] = match[t]

    return t_encodes, t_decodes


def find_utf_problems(row):
    
    try:
        if str(row.encode('UTF-8')).find('\\') != -1:
            return 1
        else:
            return 0
    except:
        return 0
    

def fix_utf_problems(row, encodes, decodes):
    
    for enc,dec in zip(encodes.keys(), decodes.keys()):
        
        try:
            if dec in row.encode():
                row = row.replace(enc, decodes[dec])
        except:
            row = row
            
    return row


def clip_to_city(data, shapefile, crs_data, x_dims, y_dims):
    data= data.rio.set_spatial_dims(x_dim=x_dims, y_dim=y_dims)

    data = data.rio.write_crs(crs_data)
    
    clipped = data.rio.clip(shapefile.geometry.apply(mapping),
                            shapefile.crs, all_touched=True, 
                            invert=False, from_disk=True)
    
    return clipped

def get_turkish_city_names():
    
    # path related to province
    il = 'common'
    
    # data source
    data_source = 'population'
    
    # define general path to datasets
    general_path = f'data/{il}/{data_source}/*'

    # get individual data links
    data_links = glob(general_path)

    # open dataframe
    dt = pd.read_excel(data_links[0])
    
    # define turkish to english encode-decode
    turkish_encodes, turkish_decodes = create_encode_and_decode()

    # fix encodes 
    dt['Province'] = dt['Province'].apply(lambda x: fix_utf_problems(x, 
                                                                     turkish_encodes,
                                                                     turkish_decodes)) \
                                                                     .str \
                                                                     .lower()
    return dt['Province'].unique()