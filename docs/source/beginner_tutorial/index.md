# Beginner's guide

This guide will walk you through the steps to step for  running **pamflow** and understanding its outputs. For this, we will use an immersive example with real acoustic data. As soon as you understand this toy example, you will be able to run t**pamflow** with your own data. The tutorial takes approximately 30 minutes to complete.

***Context: The Guaviare Project***
*The National biodiversity institute in Colombia, the Humboldt Institute, collaborated with communities at Guaviare, Colombia to perform a communitary project on the local bird fauna. You are part of the project  and your task is to process the passively collected acoustic data, extract insights and produce relevant metrics and graphics for a report on the project. You will use **pamflow** to help you.*

***Your tasks***: 
1. Get familiar with the collected data.
2. Extract metadata from each audio file and each passive acoustic sensor.
3. Check that all sensors behaved as expected.
4. Report for presence of target species in the audios.
5. Select and store audio segments with target species' vocalizations.


In the next sections, you’ll learn how to use **pamflow** to get your work done. Make sure **pamflow** and its tools are installed before you start ([instructions here](setup.md)). If you are an experienced python user and want a faster, less detailed set-up you can find it [here](../documentation/index.md).

![](../../meta/images/pamflow_intro.jpg)



```{toctree}
:maxdepth: 1
:caption: Tutorial
setup.md
input_data.md
data_preparation.md
quality_control.md
species_detection.md





