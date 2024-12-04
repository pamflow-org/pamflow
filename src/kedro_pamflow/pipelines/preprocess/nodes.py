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
import geopandas as gpd
import contextily as cx
import seaborn as sns
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
#elif args.operation == "metadata_summary":
def metadata_summary(df):
    """ Get a summary of a metadata dataframe of the acoustic sampling

    Parameters
    ----------
    df : pandas DataFrame or string with path to a csv file
        The dataframe must have the columns site, date, sample_length.
        Use maad.util.get_audio_metadata to compile the dataframe.

    Returns
    -------
    pandas DataFrame
        A summary of each site
    """
    
    #df = input_validation(df)
    

    df['date'] = pd.to_datetime(df.date,  format='%Y-%m-%d %H:%M:%S')
    df.dropna(inplace=True)
    df_summary = {}
    for site, df_site in df.groupby('sensor_name'):
        site_summary = {
            'date_ini': str(df_site.date.min()),
            'date_end': str(df_site.date.max()),
            'n_recordings': len(df_site),
            'duration': str(df_site.date.max() - df_site.date.min()),
            'time_diff': df_site['date'].sort_values().diff().median(),
            'sample_length': round(df_site.length.median(), 1),
            'sample_rate': int(df_site.sample_rate.median()),
        }
        df_summary[site] = site_summary
    df_summary = pd.DataFrame(df_summary).T
    return df_summary.reset_index().rename(columns={'index': 'sensor_name'})


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
    # Function argument validation


    # Group recordings by day
    df['date'] = pd.to_datetime(df['date']).dt.date
    df_out = df.groupby(['sensor_name', 'date']).size().reset_index(name='count')
    df_out.sort_values(by=['sensor_name', 'date'], inplace=True)

    # Reorder sites according to first recording
    # Calculate the first date for each site
    #first_date_per_site = df_out.groupby('sensor_name')['date'].min().reset_index()
    #first_date_per_site = first_date_per_site.rename(columns={'date': 'first_date_'})

    df_out['first_date']=df_out.groupby('sensor_name')['date'].transform('min')
    # Sort the DataFrame based on the first date
    df_out = df_out.sort_values(by='first_date')

    fig, ax = plt.subplots(figsize=[8,5])


    x='sensor_name'
    y='date'
    sns.scatterplot(y=y, x=x, size='count', hue='count', data=df_out, ax=ax)
    sns.scatterplot(y=y, x=x, size='count', hue='count', data=df_out, ax=ax,
                        hue_norm=(0, df_out['count'].max()),
                        size_norm=(0, df_out['count'].max()))
    ax.grid(alpha=0.2)
    ax.set_title(
        f'Sensor Deployment: {df.sensor_name.unique().shape[0]} sites | {df.shape[0]} files')

    ax.tick_params(axis='x',labelrotation=90)

    ax.legend(
        bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, title='N. Rec')
    fig.tight_layout()
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

    geo_info_microfonos=geo_info_microfonos.rename(columns={device_id:'sensor_name'})

    geo_info_microfonos =geo_info_microfonos.merge(metadata_summary,
                       on='sensor_name',
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

    for x, y, label in zip(geo_info_microfonos.geometry.x, geo_info_microfonos.geometry.y, geo_info_microfonos.sensor_name):
        ax.annotate(label, 
                    xy=(x, y), 
                    xytext=(3, 3), 
                    textcoords="offset points",
                    fontsize=0.2*geo_info_microfonos['sensor_name'].nunique(),
                    #rotation=np.random.choice([0,45,-45],p=[0.8,0.1,0.1])
                )
    return fig


                               
def get_timelapse(sensor_deployment_data, 
                  audio_metadata,
                  sample_len,
                  sample_period, 
                  plot_params ):
    #get selected date for calculating timelapse
    sensor_deployment_data['num_recordings_mean']=sensor_deployment_data.groupby('date')['count'].transform('mean')

    sensor_deployment_data['num_sensors_by_date']=sensor_deployment_data.groupby('date')['sensor_name'].transform('nunique')

    selected_date=sensor_deployment_data.sort_values(by=['num_sensors_by_date','num_recordings_mean'],
                                    ascending=[False,False]
                                    )['date'].unique()[0]
    #timelapse calculation
    audio_metadata=audio_metadata.astype({'date':'datetime64[ns]'})

    df_timelapse=audio_metadata[audio_metadata['date'].dt.date==datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()]

    df_timelapse['day']=df_timelapse['date'].dt.date

    df_timelapse.set_index('date', inplace=True)

    ngroups = df_timelapse.groupby(['sensor_name', 'day']).ngroups


    nperseg       =plot_params['nperseg']
    noverlap      =plot_params['noverlap']
    db_range      =plot_params['db_range']
    width         =plot_params['fig_width']
    height        =plot_params['fig_height']
    # create time lapse
    print(f'Processing audio timelapse for {ngroups} devices:')
    timelapse_dict={}
    spectrograms_dict={}
    for site, df_site in df_timelapse.groupby('sensor_name'):
        
        df_site.sort_values('date', inplace=True)
        df_site = df_site.resample(sample_period).first()
        df_site.dropna(inplace=True)
        long_wav, fs = concat_audio(df_site['path_audio'],
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



        
        file_name=f'{site}_timelapse_{selected_date}'
        timelapse_dict[file_name]=(long_wav, fs)
        spectrograms_dict[file_name]=fig
    return timelapse_dict, spectrograms_dict


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
        #'Latitud':,
        #'Longitud':,
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


    

