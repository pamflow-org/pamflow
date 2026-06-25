# Beginner's guide

This guide will walk you through the steps for running **pamflow** using a real-world example with actual acoustic data. Once you are familiar with this example, you will be able to run **pamflow** with your own data. The tutorial takes approximately 30 minutes to complete.

Make sure **pamflow** is installed before you start — follow the [installation instructions](setup.md). A technical reference for experienced users is available in the [documentation](../documentation/index.md).

***Context: The Guaviare Project***
*The XXXX Institute in Colombia collaborated with communities in Guaviare, Colombia to conduct a community monitoring project on local bird fauna using passive acoustic monitoring (PAM). You are part of the project and your task is to process the audio recordings, extract insights, and produce relevant metrics and visualizations for a project report.*

***Your tasks***:
1. Download and explore the data collected in the field.
2. Configure **pamflow** and prepare the data for processing.
3. Verify that all recorders performed as expected during the deployment.
4. Automatically detect target bird species in the recordings using BirdNET.
5. Extract and organize audio segments for expert validation.

![The Guaviare Project illustrative image](../../meta/images/pamflow_intro.jpg)

```{toctree}
:maxdepth: 1
:caption: Tutorial
input_data.md
data_preparation.md
quality_control.md
species_detection.md





