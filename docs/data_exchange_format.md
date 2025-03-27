To manage data colected during PAM analyses and facilitate exchange with biodiversity repositories, we implemented a standard called *pamDP*. 
This standard was adapted from [camtrapDP](https://camtrap-dp.tdwg.org/), maintaining as much as posible, yet incoporating particularities from PAM. 
The data is stored in 3 main csv tables:

| File Name        | Description |
|-----------------|-------------|
| **deployment.csv** | Stores metadata about each deployment, including location, time frame, and recorder details. |
| **media.csv**      | Contains information about recorded media files, such as file paths, timestamps, and technical metadata. |
| **observation.csv** | Records detected observations from media, including species identification, timestamps, and confidence scores. |


## Deployment
| Field Name              | Description | Required | Unique | Type | Example |
|-------------------------|-------------|----------|--------|------|---------|
| **deploymentID**        | Unique identifier for the deployment. Required for tracking and referencing specific deployments. | TRUE | TRUE | string | DEP001 |
| **locationID**          | Identifier for the deployment location, either globally unique or dataset-specific. | FALSE | TRUE | string | LOC001 |
| **locationName**        | Name assigned to the deployment location for easy reference. | FALSE | FALSE | string | Finca La Esperanza |
| **latitude**            | Latitude of the deployment location in decimal degrees (WGS84). Range: -90 to 90. | TRUE | FALSE | float | 5.270442 |
| **longitude**           | Longitude of the deployment location in decimal degrees (WGS84). Range: -180 to 180. | TRUE | FALSE | float | 2.384995 |
| **coordinateUncertainty** | Radius (in meters) representing the horizontal positional uncertainty of the deployment location. Leave blank if unknown. | FALSE | FALSE | float (> 0) | 100 |
| **deploymentStart**     | Date and time when the deployment started, formatted as ISO 8601 (YYYY-MM-DDThh:mm:ssZ or with timezone offset). | TRUE | FALSE | datetime | 2020-03-01T22:00:00Z |
| **deploymentEnd**       | Date and time when the deployment ended, formatted as ISO 8601 (YYYY-MM-DDThh:mm:ssZ or with timezone offset). | TRUE | FALSE | datetime | 2020-04-01T22:00:00Z |
| **setupBy**            | Name or identifier of the individual or organization responsible for deploying the recorder. | FALSE | FALSE | string | Juan Gómez |
| **recorderID**         | Unique identifier of the audio recorder used (e.g., serial number). | FALSE | TRUE | string | G02345 |
| **recorderModel**      | Manufacturer and model of the recorder, formatted as manufacturer-model. | TRUE | FALSE | string | Audiomoth v1.2.0 |
| **recorderDelay**      | Time (in seconds) after a detection during which further activity is ignored. Minimum value: 0. | FALSE | FALSE | float (min 0) | 120 |
| **recorderHeight**     | Height (in meters) at which the recorder was deployed. Not to be combined with `recorderDepth`. | FALSE | FALSE | float (min 0) | 1.2 |
| **recorderDepth**      | Depth (in meters) at which the recorder was deployed. Not to be combined with `recorderHeight`. | FALSE | FALSE | float (min 0) | 4.8 |
| **recorderTilt**       | Vertical tilt angle of the recorder in degrees. -90° (downward), 0° (horizontal), 90° (upward). | FALSE | FALSE | float (min -90, max 90) | 87 |
| **recorderHeading**    | Horizontal orientation of the recorder in degrees, measured clockwise from north (0° = north, 90° = east, etc.). Range: 0 to 360. | FALSE | FALSE | float (min 0, max 360) | 225 |
| **recorderConfiguration** | Detailed settings used for data collection (e.g., microphone type, recording schedule). | TRUE | FALSE | string | record 1 minute every 29 minutes, internal microphone |
| **detectionDistance**  | Maximum distance (in meters) at which the recorder reliably detects activity. Typically measured via playback experiments. | FALSE | FALSE | float (min 0) | 9.5 |
| **timestampIssues**    | Indicates whether timestamps in media resources have known issues (e.g., unknown timezone, AM/PM switch). | FALSE | FALSE | string | unknown timezone, am/pm switch |
| **baitUse**            | Specifies whether bait was used during deployment. Additional details can be provided in `deploymentTags` or `deploymentComments`. | FALSE | FALSE | binary | FALSE |
| **featureType**        | Type of feature associated with the deployment (e.g., road, trail, water source). | FALSE | FALSE | enum | waterSource |
| **habitat**            | Brief description of the habitat at the deployment location. | FALSE | FALSE | string | Humid tropical rainforest |
| **deploymentGroups**   | Groups associated with the deployment (e.g., spatial arrays, temporal sessions). Multiple values separated by \|, formatted as `key:value` pairs where applicable. | FALSE | FALSE | string | season:winter 2020 \| grid:A1 |
| **deploymentTags**     | Tags associated with the deployment. Multiple values separated by \|, optionally formatted as `key:value` pairs. | FALSE | FALSE | string | land cover:forest \| bait:food |
| **deploymentComments** | Additional comments or observations related to the deployment. | FALSE | FALSE | string | traffic noise during installation |
