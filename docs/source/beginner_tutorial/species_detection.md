## Species detection

You are almost completing your assigned tasks for The Guaviare Project. In ths new section you will learn how **pamflow** can be a great help for the remaining duites. Specifically, you will learn how to use **pamflow** for automatic species detection and identification in the collected audios, filter for the custom list of target species and store segments of the audios having relavant animal vocalizations. 


***Table of Contents***:  
1. [Species detection](#species-detection)
2. [Segments](#segments)
3. [Data annotation](#data-annotation)

### Species detection
Passive acoustic monitoring is a useful tool for assessing species presence. Using **pamflow** you can automatically process all your audiofiles in `audio_root_directory` looking for bird vocalizations. Additionally, **pamflow** will filter for the animals specified in `target_species`.  To get **pamflow** to analyze the audios in search for animal vocalizations run 

```bash
kedro run --nodes "species_detection_node, filter_observations_node"
```

this will output two files: `unfiltered_observations@pamDP` and `observations@pamDP` which follow the [observation data format](../data_exchange_format.md#getting-started) and will be stored in `data/output/species_detection/unfiltered_observations.csv` and `data/output/species_detection/observations.csv respectively`. As suggested by their names, `unfiltered_observations@pamDP` stores every detection regardless of the animal detected whereas `observations@pamDP` acconts for detections exclusively for those species in `target_species`. Each detection specifies the file and timestamp of the vocalization, along with the detected animal’s scientific name and the confidence level of the identification (classification probability). You can learn the specifics  of the `observations@pamDP` format bellow (column content, data constraints, schema...) on the [Data Exchange Formats ](../data_exchange_format.md#Observations)  section.

| File Name                     | Start Time | End Time | Scientific Name         | ... | classificationProbability |
|-------------------------------|------------|----------|-------------------------|-----|---------------------------|
| MC-002_20240302_073000.wav    | 00:36.0    | 00:39.0  | Amazona farinosa        | ... | 0.168                     |
| MC-002_20240302_073000.wav    | 00:42.0    | 00:45.0  | Cyanocorax violaceus    | ... | 0.285                     |
| MC-009_20240302_073000.wav    | 00:57.0    | 01:00.0  | Pitangus sulphuratus    | ... | 0.142                     |
| MC-013_20240302_073000.wav    | 00:36.0    | 00:39.0  | Ramphastos tucanus      | ... | 0.762                     |
| ...                           | ...        | ...      | ...                     | ... | ...                       |

### Segments

Now that the species of interest to the project have been spotted in the audios, the bird experts need to listen to some of these detections to confirm them. Instead of having the experts reading the `observations@pamDP` file to select some of the detections, looking for the original audiofiles and going to the exact second where the detection started, you can use **pamflow** to select and store the segment of each audio where there is a relevant detection. By running

```bash
kedro run --nodes "create_segments_node, create_segments_folder_node"
```

**pamflow** will randomly select a custom number of segments for each species out of the detections in `observations@pamDP`. The info of the selected segments will be stored in `segments@pandas` and the actual segments are now stored in `data/output/species_detection/segments`. Inside this path, one folder for each species in `target_species` will contain the corresponding audios for the segments.

``` 
data/
├── input/                        
└── output/                       
    ├──  species_detection/                    
        └── segments/                    
            ├── Amazona_farinosa/        
            │   ├── 0.142_MC-002_20240302_073000_57.0_60.0.WAV
            │   ├── 0.168_MC-009_20240302_073000_36.0_39.0.WAV
            │   │            ...
            │   └── 0.762_MC-013_20240302_073000_42.0_45.0.WAV      
            ├── Cyanocorax_violaceus/    
            ├── Pitangus_sulphuratus/    
            └── Ramphastos_tucanus/              
```
Each file name follows the structure `<classification probability>_<original file name>_<start time>_<end time>.WAV`. 

### Data annotation 

The segments are now ready for the experts to listen and confirm the detections. In order to make verification easier for them, **pamflow** can generate excel files referencing each of the segments. As soon as an expert determines if a particular detection is accurate or not, she only needs to type true or false on the format.  Additionally, if an observation is not accurate, experts can type the actual species in the segment (if known) on the column `detectedSpecies`. For generating these formats run 

```bash
kedro run --nodes "create_manual_annotation_formats_node"
```

This will create one excel file per species in the folder `data/input/manual_annotations`:


``` 
data/
├── input/                        
│   └── manual_annotations/       # Folder containing manual annotation files for each species
│       ├── Amazona_farinosa_manual_annotations.xlsx
│       ├── Cyanocorax_violaceus_manual_annotations.xlsx
│       ├── Pitangus_sulphuratus_manual_annotations.xlsx
│       └── Ramphastos_tucanus_manual_annotations.xlsx
└── output/             
```

| segmentsFilePath                                      | filePath                                    | classificationProbability | eventStart | eventEnd | scientificName     | positive | detectedSpecies |
|-------------------------------------------------------|---------------------------------------------|---------------------------|------------|----------|-------------------|----------|----------------|
| 0.841_MC-009_20240301_073000_36.0_39.0.WAV            | .../MC-009/MC-009_20240301_073000.WAV       | 0.841                     | 36         | 39       | Amazona farinosa  |          |                |
| 0.684_MC-009_20240301_073000_0.0_3.0.WAV              | .../MC-009/MC-009_20240301_073000.WAV       | 0.684                     | 0          | 3        | Amazona farinosa  |          |                |
| 0.659_MC-009_20240301_073000_33.0_36.0.WAV            | .../MC-009/MC-009_20240301_073000.WAV       | 0.659                     | 33         | 36       | Amazona farinosa  |          |                |
| 0.653_MC-009_20240301_073000_30.0_33.0.WAV            | .../MC-009/MC-009_20240301_073000.WAV       | 0.653                     | 30         | 33       | Amazona farinosa  |          |                |