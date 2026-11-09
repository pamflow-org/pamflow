# Is pamflow right for my project?

pamflow turns passive acoustic monitoring (PAM) recordings into structured, documented, and reusable data. This page helps you quickly decide whether it fits your needs.

## pamflow is for you if

1. Your data arrives structured: audio recordings and associated metadata.
2. You want your analysis and data to be well organized, reproducible, and ready to reuse or share.
3. You plan to combine the audio with other types of data in later analyses.
4. You want to use multiple ways to analyze and characterize the acoustic environment.

## pamflow is not

1. **An exploration environment.** It leverages the structure of your data so you can explore it in notebooks, but that is not its main function.
2. **A model training environment.** It runs existing models; it is not meant for developing new ones.
3. **A replacement for expert validation.** It uses detection models, but their results are only reliable if they are calibrated and validated for your context. Detections are candidates, not confirmations.
4. **An ecological analysis tool.** It delivers data about sounds, not ecological interpretations. Its purpose is to leave your data ready for statistical analyses, using the tools of your choice.
