## Species detection

Here you will learn how use pamflow for automatic species detection and identification in the collected audios, filter for the custom list of target species and store segmetns of the audios having relavant animal vocalizations. 


***Table of Contents***:  
1. [Species detection](#species-detection)
2. [Segments](#segments)
3. [Data annotation](#data-annotation)

### Species detection
Passive acoustic monitoring is a useful tool for assessing species presence. Using **pamflow** you can automatically process all your audiofiles in `audio_root_directory` looking for animal vocalizations. Additionally, **pamflow** will filter for the animals specified in `target_species`.  To get **pamflow** to analyze the audios in search for animal vocalizations run 

```bash
kedro run --nodes "species_detection_node, filter_observations_node"
```

this will output two files: `unfiltered_observations@pamDP` and `observations@pamDP` which follow the [observation data format](../data_exchange_format.md#getting-started) and will be stored in `data/output/species_detection/unfiltered_observations.csv` and `data/output/species_detection/observations.csv respectively`. As suggested by their names, `unfiltered_observations@pamDP` stores every detection regardless of the animal detected whereas `observations@pamDP` acconts for detections exclusively for those species in `target_species`. Each detection in both files indicates in which file is the vocalization and in what time of the audio as well as the scientific name of the animal detected and the confidence of the detection. 

| File Name                     | Start Time | End Time | Scientific Name         | ... | Confidence |
|-------------------------------|------------|----------|-------------------------|-----|------------|
| MC-002_20240302_073000.wav    | 00:36.0    | 00:39.0  | Amazona farinosa        | ... | 0.168      |
| MC-002_20240302_073000.wav    | 00:42.0    | 00:45.0  | Cyanocorax violaceus    | ... | 0.285      |
| MC-009_20240302_073000.wav    | 00:57.0    | 01:00.0  | Pitangus sulphuratus    | ... | 0.142      |
| MC-013_20240302_073000.wav    | 00:36.0    | 00:39.0  | Ramphastos tucanus      | ... | 0.762      |
| ...                           | ...        | ...      | ...                     | ... | ...        |

### Segments

Now that the species of interest to the project have been spotted in the audios, the bird experts need to listen to some of these detections to confirm the detection. Instead of having the experts reading the `observations@pamDP` file to select some of the detections, looking for the original audiofiles and going to the exact second where the detection started, you can use **pamflow** to select and store the segment of each audio where there is a relevant detection. By running

```bash
kedro run --nodes "create_segments_node, create_segments_folder_node"
```

**pamflow** will randomly select a custom number of segments for each species out of the detections in `observations@pamDP`. The info of the selected segments will be stored in `segments@pandas` and the actual segments are now stored in `data/output/species_detection/segments`. Inside this path, one folder for each species in `target_species` will contain the corresponding audios for the segments.

```plaintext
data/
├── input/                        
└── output/                       
    ├──  species_detection/                    
        └── segments/                    
            ├── Amazona_farinosa/        
            │   ├── 0.142_MC-009_20240302_073000_57.0_60.0.WAV
            │   ├── 0.168_MC-009_20240302_073000_36.0_39.0.WAV
            │   │            ...
            │   └── 0.762_MC-009_20240302_073000_42.0_45.0.WAV      
            ├── Cyanocorax_violaceus/    
            ├── Pitangus_sulphuratus/    
            └── Ramphastos_tucanus/              
```
Each file name follows the structure `<confidence>_<original file name>_<start time>_<end time>.WAV`. 

### Data annotation 

Now the segments are ready for the experts to listen and you want to make them the task of annotation easier for them. Using **panflow** you can automatically generate excel files referencing each of the segments. As soon as an expert determines if a particular detection is accurate or not, she only needs to type true or false on the format. For generating these formats run 

```bash
kedro run --nodes "create_manual_annotation_formats_node"
```

This will create one excel file per species in the folder `data/input/manual_annotations`:


```plaintext
data/
├── input/                        
│   └── manual_annotations/       # Folder containing manual annotation files for each species
│       ├── Amazona_farinosa_manual_annotations.xlsx
│       ├── Cyanocorax_violaceus_manual_annotations.xlsx
│       ├── Pitangus_sulphuratus_manual_annotations.xlsx
│       └── Ramphastos_tucanus_manual_annotations.xlsx
└── output/             
```