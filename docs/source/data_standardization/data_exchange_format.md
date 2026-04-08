# Input data standards

Standards may seem like an added layer of complexity, but they are what make data meaningful beyond the moment and place it was collected — enabling different teams, tools, and projects to speak the same language. In passive acoustic monitoring, where recordings are gathered across diverse sites, equipment, and research groups, a shared standard is what turns isolated audio files into comparable, reusable, and interoperable data.

## File organization

Recording files must be organized as follows:

- All audio should be stored in **a single main folder**.  
- The **required** file name format is: `DEPLOYMENTID_DATE_HOUR.wav`.

Optional recommendation: Within the main folder, create a subfolder for each deployment, named after the corresponding deployment.

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


## Field deployment sheet
This file provides metadata collected during the field deployment. It should be an Excel file named `field_deployments_sheet.xlsx`, with the below column names in the first row. See the [tutorial data](https://doi.org/10.5281/zenodo.16922848) for an example.

The fields listed below cover a representative set useful for most research purposes. Only 7 fields are strictly required, but providing more information is strongly advised — richer metadata greatly increases the long-term value and reusability of your data. Additional fields beyond those listed here can also be included in the sheet; following the [pamDP format](#deployments) for any extra fields is recommended for interoperability. Custom fields that do not follow pamDP naming will be preserved in your sheet but will not be carried over to the standardized pamDP output.

| Field Name              | Description | Required | Unique | Type | Example |
|-------------------------|-------------|----------|--------|------|---------|
|<u>**deploymentID**</u>| Unique identifier for the deployment. Required for tracking and referencing specific deployments. | ✅ | ✅ | `string` | DEP001
|<u>**latitude**</u>| Latitude of the deployment location in decimal degrees (WGS84). Range: -90 to 90. | ✅ |   | `float` | 5.2704 |
|<u>**longitude**</u>| Longitude of the deployment location in decimal degrees (WGS84). Range: -180 to 180. | ✅ |   | `float` | 2.3849 |
|**coordinateUncertainty**| Uncertainty of the geographic coordinates in meters. Range: >0. |   |   | `float` | 10.0 |
|<u>**recorderModel**</u>| Manufacturer and model of the recorder, formatted as manufacturer-model. | ✅ |   | `string` | Audiomoth v1.2.0 |
|<u>**recorderConfiguration**</u>| Detailed settings used for data collection (e.g., microphone type, recording schedule). | ✅ |   | `string` | record 1 minute every 29 minutes, internal microphone |
|**locationID**| Unique code that refers unambiguously to a location record. One locationID per latitude-longitude pair. |   | ✅ | `string` | LOC001 |
| **locationName**        | Name assigned to the deployment location for easy reference. |   |   | `string` | Finca La Esperanza |
| **recorderID** | Unique identifier of the audio recorder used. |   |   | `string` | REC01 |
| **recorderHeight**     | Height (in meters) at which the recorder was deployed. Not to be combined with `recorderDepth`.  Range: >0. |   |   | `float` | 1.2 |
| **habitat**            | Brief description of the habitat at the deployment location. |   |   | `string` | Humid tropical rainforest |
|<u>**deploymentStartDate**</u>| Date when the recorder was deployed in the field. Format: `YYYY-MM-DD`. | ✅ |   | `string` | 2025-05-29 |
|**deploymentStartTime**| Time when the recorder was deployed in the field. Format: `HH:MM:SS` (24h, local time). |  |   | `string` | 13:30:00 |
|<u>**deploymentEndDate**</u>| Date when the recorder was retrieved or the deployment ended. Format: `YYYY-MM-DD`. | ✅  |   | `string` | 2025-06-29 |
|**deploymentEndTime**| Time when the recorder was retrieved or the deployment ended. Format: `HH:MM:SS` (24h, local time). |   |   | `string` | 10:00:00 |
|**setupByName**| First name of the person responsible for deploying the recorder. |   |   | `string` | Juan |
|**setupByLastName**| Last name of the person responsible for deploying the recorder. |   |   | `string` | Gómez |
|**deploymentGroups**| Category assigned to the deployment (e.g., treatment vs. control, survey period). |   |   | `string` | period-t0 |
| **deploymentComments** | Additional comments or observations related to the deployment. |   |   | `string` | Traffic noise during installation |

## Target species

An optional `target_species.csv` file with a single column (`scientificName`) listing one species per row. Species must be a subset of the model's output labels. If the file is not provided or is left empty, no filtering is applied and **pamflow** will return detections for all species recognized by the model — though results should be reviewed carefully in this case, as the number of detections can be large.

---

```{note}
These three inputs — the audio folder, the field deployment sheet, and the target species file — are all that **pamflow** needs to run. The target species file is the only optional one.
```

# Output data standards

To manage data collected during PAM analyses and facilitate exchange with biodiversity repositories, we implemented a standard called **pamDP**.
This standard was adapted from [camtrapDP](https://camtrap-dp.tdwg.org/) (Bubnicki et al., 2023), preserving as much as possible while incorporating specific requirements for PAM.
The data is stored in 3 main tables in `csv` format:

* **[deployments.csv](#deployments)**: Stores metadata about each deployment, including location, time frame, and recorder details.
* **[media.csv](#media)**: Contains information about recorded media files, such as file paths, timestamps, and technical metadata.
* **[observations.csv](#observations)**: Records detected observations from media, including species identification, timestamps, and confidence scores.


## Deployments
The `deployments.csv` table tracks information about sensor placements, such as location, duration, and recording settings.

| Field Name              | Description | Required | Unique | Type | Example |
|-------------------------|-------------|----------|--------|------|---------|
| **deploymentID**        | Unique identifier for the deployment. Required for tracking and referencing specific deployments. | ✅ | ✅ | `string` | DEP001 |
| **locationID**          | Identifier for the deployment location, either globally unique or dataset-specific. |   | ✅ | `string` | LOC001 |
| **locationName**        | Name assigned to the deployment location for easy reference. |   |   | `string` | Finca La Esperanza |
| **latitude**            | Latitude of the deployment location in decimal degrees (WGS84). Range: -90 to 90. | ✅ |   | `number` | 5.2704 |
| **longitude**           | Longitude of the deployment location in decimal degrees (WGS84). Range: -180 to 180. | ✅ |   | `number` | 2.3849 |
| **coordinateUncertainty** | Radius (in meters) representing the horizontal positional uncertainty of the deployment location. Leave blank if unknown. Range: > 0 |   |   | `integer`| 100 |
| **deploymentStart**     | Date and time when the deployment started, formatted as ISO 8601 (YYYY-MM-DDThh:mm:ssZ or with timezone offset). | ✅ |   | `datetime` | 2020-03-01T22:00:00Z |
| **deploymentEnd**       | Date and time when the deployment ended, formatted as ISO 8601 (YYYY-MM-DDThh:mm:ssZ or with timezone offset). | ✅ |   | `datetime` | 2020-04-01T22:00:00Z |
| **setupBy**            | Name or identifier of the individual or organization responsible for deploying the recorder. |   |   | `string` | Juan Gómez |
| **recorderID**         | Unique identifier of the audio recorder used (e.g., serial number). |   | ✅ | `string` | G02345 |
| **recorderModel**      | Manufacturer and model of the recorder, formatted as manufacturer-model. |   |   | `string` | Audiomoth v1.2.0 |
| **recorderHeight**     | Height (in meters) at which the recorder was deployed. Not to be combined with `recorderDepth`.  Range: >0. |   |   | `number` | 1.2 |
| **recorderDepth**      | Depth (in meters) at which the recorder was deployed. Not to be combined with `recorderHeight`.  Range: >0. |   |   | `number` | 4.8 |
| **recorderTilt**       | Vertical tilt angle of the recorder in degrees. -90° (downward), 0° (horizontal), 90° (upward). Range: (min -90, max 90)|   |   | `integer` | 87 |
| **recorderHeading**    | Horizontal orientation of the recorder in degrees, measured clockwise from north (0° = north, 90° = east, etc.). Range: 0 to 360. |   |   | `integer` | 225 |
| **recorderConfiguration** | Detailed settings used for data collection (e.g., microphone type, recording schedule). |   |   | `string` | record 1 minute every 29 minutes, internal microphone |
| **timestampIssues**    | Indicates whether timestamps in media resources have known issues (e.g., unknown timezone, AM/PM switch). |   |   | `boolean` | true/false |
| **baitUse**            | Specifies whether bait was used during deployment. Additional details can be provided in `deploymentTags` or `deploymentComments`. |   |   | `boolean` |  true/false |
| **featureType**        | Type of feature associated with the deployment (e.g., roadPaved, trailHiking, waterSource). |   |   | `enum` | waterSource |
| **habitat**            | Brief description of the habitat at the deployment location. |   |   | `string` | Humid tropical rainforest |
| **deploymentGroups**   | Groups associated with the deployment (e.g., spatial arrays, temporal sessions). Multiple values separated by \|, formatted as `key:value` pairs where applicable. |   |   | `string` | season:winter 2020 \| grid:A1 |
| **deploymentTags**     | Tags associated with the deployment. Multiple values separated by \|, optionally formatted as `key:value` pairs. |   |   | `string` | land cover:forest \| bait:food |
| **deploymentComments** | Additional comments or observations related to the deployment. |   |   | `string` | traffic noise during installation |

## Media
The `media.csv` table contains references to audio or visual recordings used for classification.

| Field Name       | Description  | Required | Unique | Type | Example |
|------------------|-------------|----------|--------|------|---------|
| **mediaID**      | Unique identifier for the media file. | ✅ | ✅ | `string` | MEDIA001 |
| **deploymentID** | Identifier of the deployment associated with the media file (foreign key to `deployments.deploymentID`). | ✅ |  | `string` | DEP001 |
| **captureMethod** | Method used to capture the media file. |  |  | `enum: recordingSchedule, continuous, activityDetection` | recordingSchedule |
| **timestamp**    | Date and time when the media file was recorded, formatted as ISO 8601 with a timezone. | ✅ |  | `datetime` | 2020-03-24T11:21:46Z |
| **filePath**     | URL or relative path to the media file (external hosting or local package). | ✅ |  | `string` | https://colecciones.humboldt.org.co/rec/sonidos/IAvH-CSA-20439/G001_20211110_060000.WAV |
| **filePublic**   | TRUE if the media file is publicly accessible; leave blank if private (e.g., for privacy protection). | ✅ |  | `boolean` | TRUE |
| **fileName**     | Name of the media file. Useful for sorting files chronologically within a deployment (by `timestamp` first, then `fileName`). |  |  | `string` | AUDIO_001.wav |
| **fileMediatype** | Media type following the IANA format. | ✅ |  | `string` | audio/wav |
| **sampleRate**   | Sampling rate of the audio file in Hertz. | ✅ |  | `integer` | 44050 |
| **bitDepth**     | Bit depth (precision) of audio samples, in bits. | ✅ |  | `integer` | 16 |
| **fileLength**   | Duration of the audio file in seconds. | ✅ |  | `number` | 60 |
| **numChannels**  | Number of audio channels. | ✅ |  | `integer` | 1 |
| **favorite**     | TRUE if the media file is considered of interest (e.g., an exemplar sound). |  |  | `boolean` | TRUE |
| **mediaComments** | Notes or remarks about the media file (e.g., "corrupted file"). |  |  | `string` | corrupted file |

## Observations
The `observations.csv` table stores classified occurrences of species or events, including metadata like behavior, vocalization details, and classification confidence. 

| Field Name | Description | Required | Unique | Type | Example |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **observationID** | Unique identifier of the observation. | ✅ | ✅ | `string` | OBS001 |
| **deploymentID** | Identifier of the deployment the observation belongs to (foreign key). | ✅ | | `string` | DEP001 |
| **mediaID** | Identifier of the media file that was classified (foreign key). | | | `string` | M001 |
| **eventID** | Identifier of the event the observation belongs to. | | | `string` | sequence1 |
| **eventStart** | Start time of the signal in seconds relative to the beginning of the media. | ✅ | | `number` | 3.4 |
| **eventEnd** | End time of the signal in seconds relative to the beginning of the media. | ✅ | | `number` | 7.2 |
| **frequencyLow** | Lower limit of the frequency range in Hertz. | | | `number` | 500 |
| **frequencyHigh** | Higher limit of the frequency range in Hertz. | | | `number` | 1500 |
| **observationLevel** | Level at which the observation was classified (`media`, `event`, `interval`). | ✅ | | `enum` | interval |
| **observationType** | Category of the observation (e.g., `animal`, `rain`, `silence`, `unknown`). | ✅ | | `enum` | animal |
| **scientificName** | Scientific name of the observed individual(s). | | | `string` | Ramphastos tucanus |
| **count** | Number of recorded individuals. | | | `integer` | 2 |
| **lifeStage** | Age class of the observed individual(s) (`adult`, `subadult`, `juvenile`). | | | `enum` | adult |
| **sex** | Sex of the observed individual(s) (`female`, `male`). | | | `enum` | female |
| **behavior** | Primary sound-related behavior (pipe-separated). | | | `string` | foraging |
| **individualID** | Identifier of the observed individual. | | | `string` | RD213 |
| **individualPositionRadius** | Estimated distance from the recorder in meters. | | | `number` | 6.81 |
| **classificationMethod** | Method used to classify the observation (`human`, `machine`). | | | `enum` | human |
| **classifiedBy** | Name or ID of the person or AI algorithm that classified it. | | | `string` | BirdNET v2.3 |
| **classificationTimestamp** | Date and time of the classification (ISO 8601). | | | `datetime` | 2020-08-22T10:25:19 |
| **classificationProbability** | Degree of certainty of the classification (Range: 0-1). | | | `number` | 0.95 |
| **observationTags** | Tag(s) associated with the observation (pipe-separated). | | | `string` | signalToNoise:high |
| **observationComments** | Comments or notes about the observation. | | | `string` | |

## References
* Bubnicki JW, Norton B, Baskauf SJ, Bruce T, Cagnacci F, Casaer J, Churski M, Cromsigt JPGM, Farra SD, Fiderer C, Forrester TD, Hendry H, Heurich M, Hofmeester TR, Jansen PA, Kays R, Kuijper DPJ, Liefting Y, Linnell JDC, Luskin MS, Mann C, Milotic T, Newman P, Niedballa J, Oldoni D, Ossi F, Robertson T, Rovero F, Rowcliffe M, Seidenari L, Stachowicz I, Stowell D, Tobler MW, Wieczorek J, Zimmermann F, Desmet P (2023). Camtrap DP: an open standard for the FAIR exchange and archiving of camera trap data. Remote Sensing in Ecology and Conservation. https://doi.org/10.1002/rse2.374
