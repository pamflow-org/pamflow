# Required input data and exchange output format

## Input data: minimum required information

### File Organization

Recording files must be organized as follows:

- All audio should be stored in a single main folder.  
- Inside this main folder, create one subfolder **per recorder**.  
- The **subfolder name must match the prefix** of the audio file names.
- The **required** file name format is: `DEPLOYMENTID_DATE_HOUR.wav`.

Example: 
```
/SONABIO-23-256
   /MC001
      MC001_20250529_133000.wav
      MC001_20250529_134000.wav
   /MC002
      MC002_20250529_133500.wav
      MC002_20250529_134500.wav
```


### Field deployment sheet
This file provides metadata collected during the field deployment. It should be an Excel file named `field_deployments_sheet.xlsx`, with the following column names in the first row:

| Field Name              | Description | Required | Unique | Type | Example |
|-------------------------|-------------|----------|--------|------|---------|
|**deploymentID**| Unique identifier for the deployment. Required for tracking and referencing specific deployments. | ✅ | ✅ | `string` | DEP001
|**latitude**| Latitude of the deployment location in decimal degrees (WGS84). Range: -90 to 90. | ✅ |   | `float` | 5.2704 |
|**longitude**| Longitude of the deployment location in decimal degrees (WGS84). Range: -180 to 180. | ✅ |   | `float` | 2.3849 |
| **recorderModel**      | Manufacturer and model of the recorder, formatted as manufacturer-model. | ✅ |   | `string` | Audiomoth v1.2.0 |
| **recorderConfiguration** | Detailed settings used for data collection (e.g., microphone type, recording schedule). | ✅ |   | `string` | record 1 minute every 29 minutes, internal microphone |
|**locationID**| Unique code that refers unambiguously to a location record. One locationID per latitude-longitude pair. |   | ✅ | `string` | LOC001 |
| **locationName**        | Name assigned to the deployment location for easy reference. |   |   | `string` | Finca La Esperanza |
| **recorderHeight**     | Height (in meters) at which the recorder was deployed. Not to be combined with `recorderDepth`.  Range: >0. |   |   | `float` | 1.2 |
| **habitat**            | Brief description of the habitat at the deployment location. |   |   | `string` | Humid tropical rainforest |
|**setupBy**| Name or identifier of the individual or organization responsible for deploying the recorder.|   |   | `string` | Juan Gómez |
| **deploymentComments** | Additional comments or observations related to the deployment. |   |   | `string` | Traffic noise during installation |

### Target species
An optional target_species.csv with a single column (scientificName) listing one species per row. Species must be a subset of the model’s output labels. If the file is empty, no filtering is applied to detections.

## Data exchange format used in `pamflow`

To manage data collected during PAM analyses and facilitate exchange with biodiversity repositories, we implemented a standard called **pamDP**.
This standard was adapted from [camtrapDP](https://camtrap-dp.tdwg.org/) (Bubnicki et al., 2023), preserving as much as possible while incorporating specific requirements for PAM.
The data is stored in 3 main tables in `csv` format:

* **[deployments.csv](#deployments)**: Stores metadata about each deployment, including location, time frame, and recorder details.
* **[media.csv](#media)**: Contains information about recorded media files, such as file paths, timestamps, and technical metadata.
* **[observations.csv](#observations)**: Records detected observations from media, including species identification, timestamps, and confidence scores.


### Deployments
The `deployments.csv` table tracks information about sensor placements, such as location, duration, and recording settings.

| Field Name              | Description | Required | Unique | Type | Example |
|-------------------------|-------------|----------|--------|------|---------|
| **deploymentID**        | Unique identifier for the deployment. Required for tracking and referencing specific deployments. | ✅ | ✅ | `string` | DEP001 |
| **locationID**          | Identifier for the deployment location, either globally unique or dataset-specific. |   | ✅ | `string` | LOC001 |
| **locationName**        | Name assigned to the deployment location for easy reference. |   |   | `string` | Finca La Esperanza |
| **latitude**            | Latitude of the deployment location in decimal degrees (WGS84). Range: -90 to 90. | ✅ |   | `float` | 5.2704 |
| **longitude**           | Longitude of the deployment location in decimal degrees (WGS84). Range: -180 to 180. | ✅ |   | `float` | 2.3849 |
| **coordinateUncertainty** | Radius (in meters) representing the horizontal positional uncertainty of the deployment location. Leave blank if unknown. Range: > 0 |   |   | `float`| 100 |
| **deploymentStart**     | Date and time when the deployment started, formatted as ISO 8601 (YYYY-MM-DDThh:mm:ssZ or with timezone offset). | ✅ |   | `datetime` | 2020-03-01T22:00:00Z |
| **deploymentEnd**       | Date and time when the deployment ended, formatted as ISO 8601 (YYYY-MM-DDThh:mm:ssZ or with timezone offset). | ✅ |   | `datetime` | 2020-04-01T22:00:00Z |
| **setupBy**            | Name or identifier of the individual or organization responsible for deploying the recorder. |   |   | `string` | Juan Gómez |
| **recorderID**         | Unique identifier of the audio recorder used (e.g., serial number). |   | ✅ | `string` | G02345 |
| **recorderModel**      | Manufacturer and model of the recorder, formatted as manufacturer-model. | ✅ |   | `string` | Audiomoth v1.2.0 |
| **recorderDelay**      | Time (in seconds) after a detection during which further activity is ignored. Minimum value: 0.  Range: >0. |   |   | `float` | 120 |
| **recorderHeight**     | Height (in meters) at which the recorder was deployed. Not to be combined with `recorderDepth`.  Range: >0. |   |   | `float` | 1.2 |
| **recorderDepth**      | Depth (in meters) at which the recorder was deployed. Not to be combined with `recorderHeight`.  Range: >0. |   |   | `float` | 4.8 |
| **recorderTilt**       | Vertical tilt angle of the recorder in degrees. -90° (downward), 0° (horizontal), 90° (upward). Range: (min -90, max 90)|   |   | `float` | 87 |
| **recorderHeading**    | Horizontal orientation of the recorder in degrees, measured clockwise from north (0° = north, 90° = east, etc.). Range: 0 to 360. |   |   | `float` | 225 |
| **recorderConfiguration** | Detailed settings used for data collection (e.g., microphone type, recording schedule). | ✅ |   | `string` | record 1 minute every 29 minutes, internal microphone |
| **detectionDistance**  | Maximum distance (in meters) at which the recorder reliably detects activity. Typically measured via playback experiments. Range: >0.|   |   | `float` | 9.5 |
| **timestampIssues**    | Indicates whether timestamps in media resources have known issues (e.g., unknown timezone, AM/PM switch). |   |   | `string` | unknown timezone, am/pm switch |
| **baitUse**            | Specifies whether bait was used during deployment. Additional details can be provided in `deploymentTags` or `deploymentComments`. |   |   | `binary` |   |
| **featureType**        | Type of feature associated with the deployment (e.g., road, trail, water source). |   |   | `enum` | waterSource |
| **habitat**            | Brief description of the habitat at the deployment location. |   |   | `string` | Humid tropical rainforest |
| **deploymentGroups**   | Groups associated with the deployment (e.g., spatial arrays, temporal sessions). Multiple values separated by \|, formatted as `key:value` pairs where applicable. |   |   | `string` | season:winter 2020 \| grid:A1 |
| **deploymentTags**     | Tags associated with the deployment. Multiple values separated by \|, optionally formatted as `key:value` pairs. |   |   | `string` | land cover:forest \| bait:food |
| **deploymentComments** | Additional comments or observations related to the deployment. |   |   | `string` | traffic noise during installation |

## Media
The `media.csv` table contains references to audio or visual recordings used for classification.

| Field Name       | Description  | Required | Unique | Type | Example |
|------------------|-------------|----------|--------|------|---------|
| **mediaID**      | Unique identifier for the media file. | ✅ | ✅ | `string` | MEDIA001 |
| **deploymentID** | Identifier of the deployment associated with the media file (foreign key to `deployments.deploymentID`). |  | ✅ | `string` | DEP001 |
| **captureMethod** | Method used to capture the media file. |  |  | `enum: activityDetection, timeLapse` | timeLapse |
| **timestamp**    | Date and time when the media file was recorded, formatted as ISO 8601 with a timezone. | ✅ |  | `string` | 2020-03-24T11:21:46Z |
| **filePath**     | URL or relative path to the media file (external hosting or local package). | ✅ |  | `string` | https://colecciones.humboldt.org.co/rec/sonidos/IAvH-CSA-20439/G001_20211110_060000.WAV |
| **filePublic**   | TRUE if the media file is publicly accessible; leave blank if private (e.g., for privacy protection). | ✅ |  | `binary` | TRUE |
| **fileName**     | Name of the media file. Useful for sorting files chronologically within a deployment (by `timestamp` first, then `fileName`). | ✅ |  | `string` | AUDIO_001.wav |
| **fileMediatype** | Media type following the IANA format. | ✅ |  | `string` | audio/wav |
| **sampleRate**   | Sampling rate of the audio file in Hertz. | ✅ |  | `float` | 44.050 |
| **bitDepth**     | Bit depth (precision) of audio samples, in bits. | ✅ |  | `integer` | 16 |
| **fileLength**   | Duration of the audio file in seconds. | ✅ |  | `float` | 60 |
| **numChannels**  | Number of audio channels. | ✅ |  | `int` | 1 |
| **favorite**     | TRUE if the media file is considered of interest (e.g., an exemplar sound). |  |  | `binary` | TRUE |
| **mediaComments** | Notes or remarks about the media file (e.g., "corrupted file"). |  |  | `string` | corrupted file |

## Observations
The `observations.csv` table stores classified occurrences of species or events, including metadata like behavior, vocalization details, and classification confidence. 

| **Field Name** | **Description** | **Required** | **Unique** | **Type** | **Example** |
|---|---|---|---|---|---|
| **observationID** | Unique observation identifier. | ✅ | ✅ | `string` | obs1 |
| **deploymentID** | Deployment identifier (foreign key). | ✅ | ✅ | `string` | dep1 |
| **mediaID** | Media file identifier (foreign key, only for media-based). | | ✅ | `string` | media1 |
| **eventID** | Event identifier linking observations. | | ✅ | `string` | sequence1 |
| **observationLevel** | Classification level: `media` (file-based) or `event`. | ✅ | | `string` | media |
| **observationType** | Observation category (enum: `animal`, `human voice`, `vehicle`, `silence`, `rain`, `wind`, `unknown`, `unclassified`). | ✅ | | `string` | animal |
| **scientificName** | Scientific name of observed species. | | | `string` | *Ramphastos tucanus* |
| **count** | Number of individuals (>1). | | | `int` | 5 |
| **lifeStage** | Age class (enum: `adult`, `subadult`, `juvenile`). | | | `string` | juvenile |
| **sex** | Sex (`female`, `male`). | | | `enum: female, male` | female |
| **behavior** | Primary sound-related behavior. | | | `string` | duet |
| **vocalActivity** | Vocalization intensity (1=Low, 2=Moderate, 3=High). | | | `int` | 1 |
| **individualID** | Unique individual identifier. | | | `string` | RD123 |
| **individualPositionRadius** | Distance from recorder (m, >0). | | | `float` | 6.81 |
| **bboxTime** | Start time of vocalization in seconds. Range >0. | ✅ | | `float` | 3.5 |
| **bboxFrequency** | Start frequency in Hertz. Range >0. | | | `float` | 1500 |
| **bboxDuration** | Duration of vocalization in seconds. Range >0. | | | `float` | 10.4 |
| **bboxBandwidth** | Vocalization bandwidth in Hertz. Range >0. | | | `float` | 5400 |
| **classificationMethod** | Classification method (`human` or `machine`). | | | `string` | human |
| **classifiedBy** | Name/ID of classifier (human or AI). | | | `string` | BirdNET v2.3 |
| **classificationTimestamp** | Classification date/time (ISO 8601). | | | `datetime` | 2020-08-22T10:25:19Z |
| **classificationProbability** | Confidence level. Range: 0-1. | | | `float` | 0.95 |
| **observationTags** | Tags (e.g., `key:value` format). | | | `string` | signalToNoise:high |
| **observationComments** | Additional notes. | | | `string` | Loud unknown bird vocalization |

## References
* Bubnicki JW, Norton B, Baskauf SJ, Bruce T, Cagnacci F, Casaer J, Churski M, Cromsigt JPGM, Farra SD, Fiderer C, Forrester TD, Hendry H, Heurich M, Hofmeester TR, Jansen PA, Kays R, Kuijper DPJ, Liefting Y, Linnell JDC, Luskin MS, Mann C, Milotic T, Newman P, Niedballa J, Oldoni D, Ossi F, Robertson T, Rovero F, Rowcliffe M, Seidenari L, Stachowicz I, Stowell D, Tobler MW, Wieczorek J, Zimmermann F, Desmet P (2023). Camtrap DP: an open standard for the FAIR exchange and archiving of camera trap data. Remote Sensing in Ecology and Conservation. https://doi.org/10.1002/rse2.374
