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
    load_config, 
    metadata_summary, 
    add_file_prefix, 
    select_metadata,
    concat_audio,
    build_folder_structure,
    input_validation,
    )
import datetime

#if args.operation == "get_audio_metadata":
def get_audio_metadata(input_path #,output
):

    #add_file_prefix(folder_name=input_path, 
    #                recursive=True
    #                )


    metadata = util.get_metadata_dir(input_path, False)
    metadata.dropna(inplace=True)  # remove problematic files
    columns_names_dict={
        'path_audio':'filePath',
        'fname':'mediaID',
        #'sample_rate':,
        #'channels':,
        #'bits':,
        #'samples':,
        #'length':,
        #'fsize':,
        'sensor_name':'deploymentID',
        'date':'timestamp',
        #'time':,
    }
    media=metadata.rename(columns=columns_names_dict)
    media['fileName']=media['filePath']
    media['fileMediatype']='WAV'
    return media#df.to_csv(output, index=False)
def metadata_summary(df):
    """ Get a summary of a metadata dataframe of the acoustic sampling

    Parameters
    ----------
    df : pandas DataFrame or string with path to a csv file
    The dataframe must have the columns 'deploymentID', 
    'date_ini', 'date_end', 'n_rcordings', 'time_diff',
    'sample_length', 'sample_rate', 'duration'.
    Use maad.util.get_audio_metadata to compile the dataframe.

    Returns
    -------
    pandas DataFrame
    A summary of each site
    """

    #df = input_validation(df)
    df['timestamp'] = pd.to_datetime(df.timestamp,  format='%Y-%m-%d %H:%M:%S')
    df.dropna(inplace=True)
    df['diff']=df['timestamp'].sort_values().diff()
    df_summary=df.groupby('deploymentID')\
                .agg(
                    date_ini=('timestamp','min'),
                    date_end=('timestamp','max'),
                    n_recordings=('deploymentID','count'),
                    time_diff=('diff','median'),
                    sample_length=('length','median'),
                    sample_rate=('sample_rate','median'),
                    
                ).reset_index()
    df_summary['duration']=df_summary['date_end']-df_summary['date_ini']
    return df_summary


def plot_sensor_deployment(df):
    """ Plot sensor deployment to have an overview of the sampling

    Parameters
    ----------
    df : pandas DataFrame
        The dataframe must have the columns site, date, sample_length.
        Use maad.util.get_audio_metadata to compile the dataframe.
    ax : matplotlib.axes, optional
        Matplotlib axes fot the figure, by default None

    Returns
    -------
    matplotlib.figure
        If axes are not provided, a figure is created and figure handles are returned.
    """

    # Group recordings by day
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.date
    df_out = df.groupby(['deploymentID', 'timestamp']).size().reset_index(name='count')
    df_out.sort_values(by=['deploymentID', 'timestamp'], inplace=True)

    # Sort the DataFrame based on the first date
    df_out['first_date']=df_out.groupby('deploymentID')['timestamp'].transform('min')
    df_out = df_out.sort_values(by='first_date')

    # Plot settings
    # Dynamically adjust figure size
    unique_sensors = df_out['deploymentID'].nunique()
    unique_dates = df_out['timestamp'].nunique()
    width = min(max(6, unique_dates * 0.3), 12)  
    height = min(max(4, unique_sensors * 0.3), 9)  
    
    # Define scatter plot sizes based on 'count' (ensuring they match actual sizes)
    sizes = (df_out['count'] - df_out['count'].min() + 1) * 3  # Example scaling

    # Create a modified version of the 'Blues' colormap
    Blues_mod = mpl.colors.LinearSegmentedColormap.from_list("Blues_mod", 
                                                              ["#b0c4de", "#08306b"])
    x='timestamp'
    y='deploymentID'
    
    # Draw scatterplot
    fig, ax = plt.subplots(figsize=[width, height])
    scatter = ax.scatter(
        df_out[x], df_out[y], s=sizes, c=df_out['count'], cmap=Blues_mod, alpha=0.9)

    # Format date
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))  # Every 7 days
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    # Add title and set grid
    ax.grid(alpha=0.2)
    ax.set_title(f'Sensor Deployment: {df.deploymentID.nunique()} sites | {df.shape[0]} files')
    
    # Create legend handles
    legend_values = np.linspace(df_out['count'].min(), df_out['count'].max(), num=4).astype(int)
    legend_handles = [
        plt.scatter([], [], s=(val - df_out['count'].min() + 1) * 3, 
                    color=Blues_mod((val - df_out['count'].min()) / (df_out['count'].max() - df_out['count'].min())),
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
    
    return fig, df_out


def plot_sensor_location(metadata,
                         metadata_summary,
                         sensor_location,
                         plot_parameters,
                         deployment_parameters
                         ):
    device_id=   deployment_parameters['device_id']
    latitude_col=deployment_parameters['latitude_col']
    longitude_col=deployment_parameters['longitude_col'] 


    #sensor_location[latitude_col]=sensor_location[latitude_col].str.replace(',','.')
    #sensor_location[longitude_col]=sensor_location[longitude_col].str.replace(',','.')
    geo_info_microfonos = gpd.GeoDataFrame(
        sensor_location[[device_id, latitude_col, longitude_col]], 
        geometry=gpd.points_from_xy(sensor_location[longitude_col],sensor_location[latitude_col], ), crs="EPSG:4326"
    )

    geo_info_microfonos=geo_info_microfonos.rename(columns={device_id:'deploymentID'})
    geo_info_microfonos['deploymentID']=geo_info_microfonos['deploymentID'].str.split(' | ').str[0]
    geo_info_microfonos =geo_info_microfonos.merge(metadata_summary,
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
                    fontsize=0.6*geo_info_microfonos['deploymentID'].nunique(),
                    #rotation=np.random.choice([0,45,-45],p=[0.8,0.1,0.1])
                )
    return fig


                               
def get_timelapse_old(sensor_deployment_data, 
                  audio_metadata,
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
    audio_metadata=audio_metadata.astype({'timestamp':'datetime64[ns]'})

    df_timelapse=audio_metadata[audio_metadata['timestamp'].dt.date==datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()]

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
    timelapse_dict={}
    spectrograms_dict={}
    import sys
    for site, df_site in df_timelapse.groupby('deploymentID'):
        
        df_site.sort_values('timestamp', inplace=True)
        df_site = df_site.resample(sample_period).first()
        df_site.dropna(inplace=True)
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
        timelapse_dict[file_name]=(long_wav, fs)
        spectrograms_dict[file_name]=fig
    return timelapse_dict, spectrograms_dict
def get_timelapse(sensor_deployment_data, 
                  audio_metadata,
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
    audio_metadata=audio_metadata.astype({'timestamp':'datetime64[ns]'})

    df_timelapse=audio_metadata[audio_metadata['timestamp'].dt.date==datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()]

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
        df_site.dropna(inplace=True)
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
        
        
    


def plantilla_usuario_to_deployment(plantilla_usuario):
    plantilla_usuario['Nombre del instalador+Apellido  del instalador']=plantilla_usuario['Nombre del instalador']+plantilla_usuario['Apellido  del instalador']

    columns_names_map={
        #'Nombre de la carpeta proyecto (NOMBRE_AÑO)':,
        'Indicador de evento':'deploymentID',
        'Fecha inicial':'deploymentStart',
        'Fecha final':'deploymentEnd',
        #'País':,
        #'Departamento':,
        #'Municipio':,
        #'Localidad':,
        'Latitud':'latitude',
        'Longitud':'longitude',
        #'Numero de archivos':,
        #'Nombre del responsable + Apellido  del responsable':'setupBy',
        'Equipo de grabación':'recorderModel',
        #'Definiciones!D17':,
        #'Elevación':,
            #'Calidad de grabación':,
        #'Nombre del proyecto':,
        'Comentario de sonido':'deploymentComments',
        #'Duración de cada grabación':,
        #'Configuración de muestreo':,
        'Hábitat':'habitat',
        #'Área Natural Protegida':,
        'Nombre del instalador+Apellido  del instalador':'setupBy',
        #'Apellido  del instalador':,
        #'Publicado':,
        #'Estrato de Vegetación':,
    }

    #'locationID'
    #'locationName'
    deployment=plantilla_usuario[columns_names_map.keys()].rename(columns=columns_names_map)

    schema={
        'deploymentID':str,
        'deploymentStart':'datetime64[ns]',
        'deploymentEnd'  :'datetime64[ns]',
        'recorderModel':str,
        'deploymentComments':str,
        'habitat':str,
        'setupBy':str,

    }
    deployment=deployment.astype(schema)    
    return deployment


    

