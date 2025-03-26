#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""
import os
import argparse
import matplotlib.pyplot as plt
from maad import sound, util
import pandas as pd
import numpy as np
import geopandas as gpd
import contextily as cx
import matplotlib.dates as mdates
import matplotlib as mpl
from kedro_pamflow.pipelines.preprocess.utils import (

    concat_audio
    )
import datetime


def get_media_file(input_path 
):

    #add_file_prefix(folder_name=input_path, 
    #                recursive=True
    #                )


    metadata = util.get_metadata_dir(input_path, False)
    metadata.dropna(inplace=True)  # remove problematic files
    print(metadata.columns)
    columns_names_dict={
        'path_audio':'filePath',
        'fname':'mediaID',
        'bits':'bitDepth',
        'sample_rate':'sampleRate',
        'length':'fileLength',
        'channels':'numChannels',
        'sensor_name':'deploymentID',
        'date':'timestamp'
    }
    media=metadata.rename(columns=columns_names_dict)
    media['fileName']=media['filePath'].str.split(os.sep).str[-1]
    media['fileMediatype']='WAV'
    media['mediaComments']=None
    media['favorite']=None
    media[ 'captureMethod']='activityDetection'

    return media.drop(columns=['time','fsize','samples'])
def get_media_summary(media):
    """ Get a summary of a metadata dataframe of the acoustic sampling

    Parameters
    ----------
    df : A dataframe following pamDP.media data standards.

    Returns
    -------
    pandas DataFrame
    A summary of each site
    """

    media['timestamp'] = pd.to_datetime(media.timestamp,  format='%Y-%m-%d %H:%M:%S')
    
    media['diff']=media['timestamp'].sort_values().diff()
    media_summary=media.groupby('deploymentID')\
                .agg(
                    date_ini=('timestamp','min'),
                    date_end=('timestamp','max'),
                    n_recordings=('deploymentID','count'),
                    time_diff=('diff','median'),
                    sample_length=('fileLength','median'),
                    sample_rate=('sampleRate','median'),
                    
                ).reset_index()
    media_summary['duration']=media_summary['date_end']-media_summary['date_ini']
    return media_summary


def plot_sensor_deployment(media):
    """ Plot sensor deployment to have an overview of the sampling

    Parameters
    ----------
    media : pandas DataFrame
        A dataframe following pamDP.media data standards.
    ax : matplotlib.axes, optional
        Matplotlib axes fot the figure, by default None

    Returns
    -------
    matplotlib.figure
        If axes are not provided, a figure is created and figure handles are returned.
    """

    # Group recordings by day
    media['timestamp'] = pd.to_datetime(media['timestamp']).dt.date
    media_out = media.groupby(['deploymentID', 'timestamp']).size().reset_index(name='count')
    media_out.sort_values(by=['deploymentID', 'timestamp'], inplace=True)

    # Sort the DataFrame based on the first date
    media_out['first_date']=media_out.groupby('deploymentID')['timestamp'].transform('min')
    media_out = media_out.sort_values(by='first_date')

    # Plot settings
    # Dynamically adjust figure size
    unique_sensors = media_out['deploymentID'].nunique()
    unique_dates = media_out['timestamp'].nunique()
    width = min(max(6, unique_dates * 0.3), 12)  
    height = min(max(4, unique_sensors * 0.3), 9)  
    
    # Define scatter plot sizes based on 'count' (ensuring they match actual sizes)
    sizes = (media_out['count'] - media_out['count'].min() + 1) * 3  # Example scaling

    # Create a modified version of the 'Blues' colormap
    Blues_mod = mpl.colors.LinearSegmentedColormap.from_list("Blues_mod", 
                                                              ["#b0c4de", "#08306b"])
    x='timestamp'
    y='deploymentID'
    
    #Order dataframe to get ordered vertical axis
    media_out=media_out.sort_values(by=y, ascending=False)

    # Draw scatterplot
    fig, ax = plt.subplots(figsize=[width, height])
    scatter = ax.scatter(
        media_out[x], media_out[y], s=sizes, c=media_out['count'], cmap=Blues_mod, alpha=0.9)

    # Format date
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))  # Every 7 days
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    # Add title and set grid
    ax.grid(alpha=0.2)
    ax.set_title(f'Sensor Deployment: {media.deploymentID.nunique()} sites | {media.shape[0]} files')
    
    # Create legend handles
    legend_values = np.linspace(media_out['count'].min(), media_out['count'].max(), num=4).astype(int)
    legend_handles = [
        plt.scatter([], [], s=(val - media_out['count'].min() + 1) * 3, 
                    color=Blues_mod((val - media_out['count'].min()) / (media_out['count'].max() - media_out['count'].min())),
                    label=f'{int(val)}') 
        for val in legend_values
    ]
    # Adjust spines
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)  # Adjust the thickness
        spine.set_color("gray")   # Change color to lighter gray

    # Add legend outside the plot
    ax.legend(handles=legend_handles, title="N. Rec", loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig, media_out


def plot_sensor_location(media_summary,
                         deployments,
                         plot_parameters
                         ):
    geo_info_microfonos = gpd.GeoDataFrame(
    deployments[['deploymentID', 'latitude', 'longitude']], 
    geometry=gpd.points_from_xy(deployments['longitude'],deployments['latitude'], ), crs="EPSG:4326"
    )


    geo_info_microfonos =geo_info_microfonos.merge(media_summary,
                    on='deploymentID',
                    how='left'
                    )

    geo_info_microfonos=geo_info_microfonos.astype({'n_recordings':'float64'})

    fig,ax=plt.subplots(figsize=(10,10))
    geo_info_microfonos.plot(ax=ax,
                            #c=geo_info_microfonos['n_recordings'],
                            column='n_recordings',
                            cmap=plot_parameters['colormap'],
                            legend=True
                            
                            )

    #ax.legend(metadata_summary['n_recordings'])

    ax.set_title('Number of recordings per sensor')

    cx.add_basemap(ax, 
                #source=xyz.OpenStreetMap.Mapnik,
                crs=geo_info_microfonos.crs.to_string()
                )

    for x, y, label in zip(geo_info_microfonos.geometry.x, geo_info_microfonos.geometry.y, geo_info_microfonos.deploymentID):
        ax.annotate(label, 
                    xy=(x, y), 
                    xytext=(3, 3), 
                    textcoords="offset points",
                    fontsize=0.15*geo_info_microfonos['deploymentID'].nunique(),
                    #rotation=np.random.choice([0,45,-45],p=[0.8,0.1,0.1])
                )
    return fig


def get_timelapse(sensor_deployment_data, 
                  media,
                  sample_len,
                  sample_period, 
                  plot_params ):
    #get selected date for calculating timelapse
    sensor_deployment_data['num_recordings_mean']=sensor_deployment_data.groupby('timestamp')['count'].transform('mean')

    sensor_deployment_data['num_sensors_by_date']=sensor_deployment_data.groupby('timestamp')['deploymentID'].transform('nunique')

    selected_date=sensor_deployment_data.sort_values(by=['num_sensors_by_date','num_recordings_mean'],
                                    ascending=[False,False]
                                    )['timestamp'].unique()[0]
    #timelapse calculation
    media=media.astype({'timestamp':'datetime64[ns]'})

    df_timelapse=media[media['timestamp'].dt.date==datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()]

    df_timelapse['day']=df_timelapse['timestamp'].dt.date

    df_timelapse.set_index('timestamp', inplace=True)

    ngroups = df_timelapse.groupby(['deploymentID', 'day']).ngroups


    nperseg       =plot_params['nperseg']
    noverlap      =plot_params['noverlap']
    db_range      =plot_params['db_range']
    width         =plot_params['fig_width']
    height        =plot_params['fig_height']
    # create time lapse
    print(f'Processing audio timelapse for {ngroups} devices:')
    import sys
    for site, df_site in df_timelapse.groupby('deploymentID'):
        
        df_site.sort_values('timestamp', inplace=True)
        df_site = df_site.resample(sample_period).first()

        long_wav, fs = concat_audio(df_site['filePath'],
                                    sample_len=sample_len, 
                                )
        plt.close()
        fig,ax=plt.subplots(figsize=(width,height))
        Sxx, tn, fn, ext = sound.spectrogram(long_wav,
                                            fs,
                                            nperseg=nperseg,
                                            noverlap=noverlap#nperseg*noverlap
                                            )
        util.plot_spectrogram(Sxx, 
                                        ext, 
                                        db_range, 
                                        ax=ax,
                                        colorbar=False
                                        )



        print('='*20)
        print('='*20)
        print('='*20)
        print(f'long_wav {site}',sys.getsizeof(long_wav)/10**9)
        print(f'fig {site}',sys.getsizeof(fig)/10**9)
        print('='*20)
        print('='*20)
        print('='*20)

        file_name=f'{site}_timelapse_{selected_date}'
        yield {file_name:(long_wav, fs)},{file_name:fig}
        
        
    


def plantilla_usuario_to_deployment(plantilla_usuario, media_summary):
    plantilla_usuario['Nombre del instalador+Apellido  del instalador']=plantilla_usuario['Nombre del instalador']+plantilla_usuario['Apellido  del instalador']

    columns_names_map={
        
        'Indicador de evento':'deploymentID',
        'Fecha inicial':'deploymentStart',
        'Fecha final':'deploymentEnd',
        'Localidad':'locationName', 
        'Latitud':'latitude',
        'Longitud':'longitude',
        'Equipo de grabación':'recorderModel',
        'Comentario de sonido':'deploymentComments',
        'Configuración de muestreo':'recorderConfiguration',
        'Hábitat':'habitat',
        'Nombre del instalador+Apellido  del instalador':'setupBy',
    }
      
    
    
    
    
    
   
    deployment=plantilla_usuario[columns_names_map.keys()].rename(columns=columns_names_map)
    
    
    deployment['recorderID']=None
    deployment['locationID']=deployment['locationName']
    deployment['recorderHeight']=None 
    deployment['coordinateUncertainty'] =None
    deployment['deploymentGroups']=None 

    #Fill missing values in required columns
    deployment=deployment.fillna({'recorderConfiguration':'record 1 minute every 29 minutes, internal microphone',
                    'recorderModel':'Audiomoth - 1.2',
                    
                    })

    media_summary=media_summary[['deploymentID','date_ini','date_end']]

    deployment=deployment.merge(media_summary,
                    on='deploymentID',
                    how='left'
                    )

    deployment['deploymentStart']=deployment['deploymentStart'].combine_first(deployment['date_ini'])
    deployment['deploymentEnd']=deployment['deploymentEnd'].combine_first(deployment['date_end'])

    deployment=deployment.dropna(subset=['deploymentStart','deploymentEnd','deploymentID'])

    deployment=deployment.drop(columns=['date_ini','date_end'])
    
      
    return deployment


    

