""" Utility functions to compute acoustic indices """

import os
import concurrent.futures
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from maad import sound, features, util


def compute_acoustic_indices(s, Sxx, tn, fn):
    """ 
    Main function that defines which and how indices will be computed.
    
    Parameters
    ----------
    s : 1d numpy array
        acoustic data
    Sxx : 2d numpy array of floats
        Amplitude spectrogram computed with maad.sound.spectrogram mode='amplitude'
    tn : 1d ndarray of floats
        time vector with temporal indices of spectrogram.
    fn : 1d ndarray of floats
        frequency vector with temporal indices of spectrogram..

    Returns
    -------
    df_indices : pd.DataFrame
        Acoustic indices
    """
    
    # Set spectro as power (PSD) and dB scales.
    Sxx_power = Sxx**2
    Sxx_dB = util.amplitude2dB(Sxx)

    # Compute acoustic indices
    ADI = features.acoustic_diversity_index(
        Sxx, fn, fmin=0, fmax=24000, bin_step=1000, index='shannon', dB_threshold=-40)
    _, _, ACI = features.acoustic_complexity_index(Sxx)
    NDSI, xBA, xA, xB = features.soundscape_index(
        Sxx_power, fn, flim_bioPh=(2000, 20000), flim_antroPh=(0, 2000))
    Ht = features.temporal_entropy(s)
    Hf, _ = features.frequency_entropy(Sxx_power)
    H = Hf * Ht
    BI = features.bioacoustics_index(Sxx, fn, flim=(2000, 11000))
    NP = features.number_of_peaks(Sxx_power, fn, mode='linear', min_peak_val=0, 
                                  min_freq_dist=100, slopes=None, prominence=1e-6)
    SC, _, _ = features.spectral_cover(Sxx_dB, fn, dB_threshold=-70, flim_LF=(1000,20000))
    
    # Structure data into a pandas series
    df_indices = pd.Series({
        'ADI': ADI,
        'ACI': ACI,
        'NDSI': NDSI,
        'BI': BI,
        'Hf': Hf,
        'Ht': Ht,
        'H': H,
        'SC': SC,
        'NP': int(NP)})

    return df_indices


#%%
def compute_acoustic_indices_single_file(
        path_audio, target_fs=48000, filter_type=None, filter_cut=None, filter_order=None,
        verbose=True):
    
    if verbose:
        print(f'Processing file {path_audio}', end='\r')

    # load audio
    s, fs = sound.load(path_audio)
    s = sound.resample(s, fs, target_fs, res_type='scipy_poly')
    if filter_type is not None:
        s = sound.select_bandwidth(s, target_fs, ftype=filter_type, fcut=filter_cut, forder=filter_order)

    # Compute the amplitude spectrogram and acoustic indices
    Sxx, tn, fn, _ = sound.spectrogram(
        s, target_fs, nperseg = 1024, noverlap=0, mode='amplitude')
    df_indices_file = compute_acoustic_indices(s, Sxx, tn, fn)
    
    return df_indices_file

#%%
def batch_compute_acoustic_indices(data, path_save=None):
    df = input_validation(data)
    sensor_list = df.sensor_name.unique()
    
    # Loop through sites
    for sensor_name in sensor_list:
        flist_sel = df.loc[df.sensor_name==sensor_name,:]
        
        df_indices = pd.DataFrame()
        for idx_row, row in flist_sel.iterrows():
            print(f'{idx_row+1} / {flist_sel.index[-1]}: {row.fname}', end='\r')
            # Load and resample if needed
            df_indices_file = compute_acoustic_indices_single_file(row.path_audio)
                
            # add file information to dataframes
            add_info = row[['fname', 'sensor_name', 'date']]
            df_indices_file = pd.concat([add_info, df_indices_file])
            
            # append to dataframe
            df_indices = pd.concat([df_indices, df_indices_file.to_frame().T])
            
        # Save dataframes
        df_indices.to_csv(path_save+sensor_name+'_indices.csv', index=False)

#%% Parellel computing
def compute_indices_parallel(data, target_fs, filter_type, filter_cut, filter_order, n_jobs=4):
    
    if n_jobs == -1:
        n_jobs = os.cpu_count()

    print(f'Computing acoustic indices for {data.shape[0]} files with {n_jobs} threads')
    
    # Use concurrent.futures for parelell execution
    files = data.path_audio.to_list()
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_jobs) as executor:
        
        # Use submit for each task
        futures = {executor.submit(compute_acoustic_indices_single_file, file, target_fs, filter_type, filter_cut, filter_order): file for file in files}

        # Get results when tasks are completed
        results = []
        for future in concurrent.futures.as_completed(futures):
            file_path = futures[future]
            try:
                result = future.result()
                result['fname'] = os.path.basename(file_path)
                results.append(result)
            
            except Exception as e:
                print('='*10)
                print('='*10)
                print(f"Error processing {file_path}: {e}")
                print('='*10)
                print('='*10)


    # Build dataframe with results
    df_out = pd.DataFrame(results)
    return df_out

#%% Sequential computing
def compute_indices_sequential(data, target_fs, filter_type, filter_cut, filter_order):
    df = input_validation(data)
    print(f'Computing acoustic indices for {df.shape[0]} files')
    
    files = df.path_audio.to_list()
    results = []
    for i, file_path in enumerate(files, start=1):
        result = compute_acoustic_indices_single_file(
            file_path, target_fs, filter_type, filter_cut, filter_order)
        result['fname'] = os.path.basename(file_path)
        results.append(result)
    
    # Build dataframe with results
    df_out = pd.DataFrame(results)
    return df_out

