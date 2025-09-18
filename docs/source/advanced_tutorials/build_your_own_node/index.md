# How to build your own node in **pamflow** 

The documentation on [previous tutorial](../../tutorial/index.md) covered all basic **pamflow's**  functionalities through a simple example on available data. For the sake of continuity, this tutorial will be based on the same data but covering functionalities  relevant users trained in python coding. Due to  this we assume you are already fammiliar with the data  and already ran **pamflow** with it. Hopefully, at the end you will be able to extend **pamflow** to cover the specific of your project.



***Context: Continuation of The Guaviare Project***
*The National biodiversity institute in Colombia, the Humboldt Institute, collaborated with communities at Guaviare, Colombia to perform a communitary project on the local bird fauna. You already processed all the passively collected acoustic data and based on your resulting insights, you now want to calculate some statistics on the detections. Instead of taking the outputs and working with them independently from **pamflow**, you will leverage its convenient architecture and functionalities to complete your task.*

***Your tasks***: 
1. Generate a table showing the daily activity pattern for each target species.
2. Generate spider plots showing daily activity patterns for the target species.
3. Generate KDE plots showing daily activity patterns for the target species.



On each of the followig sections you will find relevant information on how to use **pamflow** to complete all of your tasks. Next session is devoted to show you how to use  **pamflow's** jupyter notebook kernel to keep your code development clean. 

![](../../meta/images/pamflow_intro.jpg)



```{toctree}
:maxdepth: 1
:caption: Advanced tutorial
notebook.md
custom_pipeline.md





