from glob import glob

import geopandas as gpd
import numpy as np
import pandas as pd
import rioxarray
import xarray as xr

from utils import *


def clip_subroutine(dt, province, x_dims, y_dims):
    """
    subroutine to clip data to specific province
    """
    # projection and coordinate info
    dt_proj = dt.rio.crs
    
    # open shapefile data
    shapefile_path = r'data/shapefiles/Iller_HGK_6360_Kanun_Sonrasi.shp'
    shapefile = gpd.read_file(shapefile_path)
        
    # define turkish to english encode-decode
    turkish_encodes, turkish_decodes = create_encode_and_decode()
    
    # fix utf for the province column of the dataframe
    shapefile['IL'] = shapefile['IL'].apply(
        lambda x: fix_utf_problems(x, turkish_encodes, turkish_decodes)
    ).str.lower()
    
    # check province name
    if province not in shapefile['IL'].unique():
        raise 'Inappropriate province name chosen'
    
    # query correspondent province from shapefile
    province_shp = shapefile.query(f'IL == "{province}"')
    
    # clip data to correspondent province
    clipped_dt = clip_to_city(dt, province_shp, dt_proj, x_dims, y_dims)
    return clipped_dt
    
def retrieve_dmsp(province):
    """
    Adjusts and retrieves dmsp-ols light dataset
        of corresponding province.
    """
    
    # path related to province
    il = 'common'
    
    # data source
    data_source = 'dmsp'
    
    # nearest lon and lat information (to decrease data size)
    lats = slice(42, 37)
    lons = slice(25, 35)
    
    # define general path to datasets
    general_path = f'data/{il}/{data_source}/*'

    # get individual data links
    data_links = glob(general_path)

    dt_list = []
    for link in data_links:
        
        # open data
        dt = rioxarray.open_rasterio(link) \
                      .squeeze() \
                      .sel(y = lats, 
                           x = lons)   

        # assign date information
        dt = define_dmsp_date(dt, link)
        
        # accumulate datasets
        dt_list.append(dt)
    
    # merge datasets
    merged_dt = xr.concat(dt_list, dim='time')    
    
    # assign data source and province attribute
    merged_dt = merged_dt.assign_attrs({'data-source': data_source})
    merged_dt = merged_dt.assign_attrs({'province':province})
    
    # coordinate names
    x_dims = 'x'
    y_dims = 'y'
    
    # short-cut clip to province
    clipped_dt = clip_subroutine(merged_dt, province, x_dims, y_dims)
    
    return clipped_dt


def retrieve_population(province):
    """
    Adjusts and retrieves population dataset
        of corresponding province.
    """
    
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
    # get province data
    dt = dt.query(f'Province == "{province}"').reset_index(drop=True)
    dt.attrs['data-source'] = data_source
    dt.attrs['province'] = province
    
    return dt


def retrieve_station(province):
    """
    Adjusts and retrieves station dataset
        of corresponding province.
    """
    
    data_source = 'station'
    var_name = 'T' # possible: T
    unit = 'degC'

    # define general path to datasets
    general_path = f'data/{province}/{data_source}/{var_name}.xlsx'

    # get individual data links
    data_links = glob(general_path)

    # open dataframe
    dt = pd.read_excel(data_links[0])
    
    # set attributes
    dt.attrs['data-source'] = data_source
    dt.attrs['var-name'] = var_name
    dt.attrs['unit'] = unit
    dt.attrs['province'] = province
    
    return dt


def retrieve_corine(province):
    """
    Adjusts and retrieves corine dataset
        of corresponding province.
    """
    
    # path related to province
    il = 'common'
    
    # data source
    data_source = 'corine'
    
    # nearest lon and lat information (to decrease data size)
    x = slice(48000,56000)
    y = slice(31000,40000)
    
    # define general path to datasets
    general_path = f'data/{il}/{data_source}/*'

    # get individual data links
    data_links = glob(general_path)
    
    dt_list = []
    for link in data_links:
        
        # open data
        dt = rioxarray.open_rasterio(link,
                                     chunks='10mb') \
                      .squeeze() \
                      .isel(x=x, 
                            y=y)
        
        # define date of the current data
        dt = define_corine_date(dt, link)
        
        #accumulate datasets
        dt_list.append(dt)
        
    # merge datasets
    merged_dt = xr.concat(dt_list, dim='time')    
    
    # assign data source and province attribute
    merged_dt = merged_dt.assign_attrs({'data-source': data_source})
    merged_dt = merged_dt.assign_attrs({'province':province})
    
    # coordinate names
    x_dims = 'x'
    y_dims = 'y'
    
    # short-cut clip to province
    clipped_dt = clip_subroutine(merged_dt, province, x_dims, y_dims)
    
    # turn nodata into np.nan
    nodata = clipped_dt.rio.nodata
    clipped_dt = clipped_dt.where(clipped_dt != nodata,
                                  np.nan)
    
    return clipped_dt


def retrieve_modis(province, source_type):
    """
    Adjusts and retrieves modis dataset
        of corresponding province.
    """
    
    tile_dict = {
        'istanbul': 'h20v04',
        'ankara': 'h20v04', # change
        'izmir': 'h20v04' # change
    }
    data_source = 'modis'
    tile_extension = tile_dict[province]
    var_name = 'LST_Day_1km'
    
    # define general path to datasets
    general_path = f'data/{province}/{data_source}/{source_type}/*{tile_extension}*'

    # get individual data links
    data_links = glob(general_path)

    # open each data and merge them
    dt_list = []
    
    for link in data_links:

        # open dataset
        dt = rioxarray.open_rasterio(link, masked=True).squeeze()#[var_name]

        # assign dates to modis data (the date information is not robust)
        dt = define_modis_date(dt, link)

        # accumulate each dataset
        dt_list.append(dt)
        
    # merge data
    merged_dt = xr.concat(dt_list, dim='time')
    
    # multiply data with scale factor
    scale_factor = merged_dt.attrs['scale_factor']
    merged_dt = merged_dt * scale_factor
    
    # clip data to province
    x_dims = 'x'
    y_dims = 'y'
    clipped_dt = clip_subroutine(merged_dt, 
                                 province, 
                                 x_dims, 
                                 y_dims).squeeze()
    
    return clipped_dt