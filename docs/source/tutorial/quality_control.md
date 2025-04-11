# Quality control

 Many things can go wrong during a PAM  project: a recorder can run out off battery,  break after the installation for external factors, not be installed in the right way and many more. In this section you will learn how to use **pamflow**  to check  all deployed  sensors behaved as expected.

## Table of Contents
1. [Sensor performance](#sensor-performance)
2. [Sensor location](#sensor-location)
3. [Timelapses](#timelapses)

# Sensor performance
Recall that the {{number_of_sensors}} installed sensors where  programmed for recording one minute each 30 minutes for {{number_of_days}} days. We would expect then that every sensor recorded 48 one-minute files. You can easilly and visually check if this behaviour was met using **pamflow** by typing 

```bash
kedro run --nodes plot_sensor_performance
```

in the command line. 

Now the process is over we can check for the result in the path `data\output\quality_control\sensor_performance.png`

 ![](../../meta/images/sensor_performance.png)

 Each dot in this plot represents the total recorded  minutes for one sensor in one day out of the {{number_of_days}} days the sensors were recording. The size of the dot is proportional to this quantity. In a perfect scenario every point should be the same size and all representing 48 minutes. More than 48 minutes in one sensor might be due to involuntary activation previous to the installation or due to wrong programmation. Less than 48 minutes might mean the sensor ran out of battery or broke during deployment. In any of these cases, further examination is required. Anyhow, **pamflow** is a powerfull tool to detect such problems easily.  
# Sensor location

In order to check the coordinates for each sensor  **pamflow** creates a map of the installed sensors. This map also depicts the number of total recordings. To obtain the map run 
```bash
kedro run --nodes plot_sensor_location
```
and check for the output in `data\output\quality_control\sensor_location.png`

 ![](../../meta/images/sensor_location.png)
# Timelapses

Despite of having the coordinates right and the correct recording time, the quality of the recordings might still be under a desiered standard. A physical object might be blocking the sounds or the microphone might be somehow broken. To check this without listening to  each of the recordings yourself you can generate a timelapse using **pamflow**. A timelapse summarizes the acoustic activity on one day. Using a date of good enough overall acoustic activity among the sensors, **panflows** generates an audio file for each sensor consisting of 5 seconds out of each recorded audio by that sensor at that day. Along with the audio, **pamflow** generates the corresponding spectrograms. To obtain the timelapses for each sensor run 

```bash
kedro run --nodes get_timelapse_node
```

Both the resulting audio and spectrograms can be found  in `data\output\quality_control\timelapse`

```plaintext
data/
├── input/                        
└── output/                       
    ├── acoustic_indices/         
    ├── data_preparation/         
    ├── figures/                  
    ├── graphical_soundscape/     
    ├── quality_control/          
    │   ├── sensor_location.png   
    │   ├── sensor_performance.png # Plot showing sensor performance
    │   ├── sensor_performance_data.csv # Data file for sensor performance
    │   └── timelapse/            # Timelapse outputs for quality control
    │       ├── MC-002_timelapse_2024-03-02.png  # Spectrogram for sensor MC-002
    │       ├── MC-002_timelapse_2024-03-02.WAV  # Timelapse audio for sensor MC-002
    │       ├── MC-009_timelapse_2024-03-02.png  # Spectrogram for sensor MC-009
    │       ├── MC-009_timelapse_2024-03-02.WAV  # Timelapse audio for sensor MC-009
    │       ├── MC-013_timelapse_2024-03-02.png  # Spectrogram for sensor MC-013
    │       └── MC-013_timelapse_2024-03-02.WAV  # Timelapse audio for sensor MC-013
    └── species_detection/               
```

And the resulting spectrograms should look like this
 ![](../../meta/images/MC-002_timelapse_2024-03-02.png)


In the [next](./species_detection.md) section you will learn how to use **pamflow** for detecting target species in your audios.