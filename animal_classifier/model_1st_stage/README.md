# Introduction
This part of the project is used just to generate dataset for 1st stage animal detection. </br>
Generally you should just use included animal_classifier/mcu/lib/animal-binary-classifier.zip model.</br>


[Edge Impulse model](https://studio.edgeimpulse.com/public/780187/live)

# Dataset generation
* Folder structure for dataset looks like this:
```
model_1st_stage
- dataset
    - animals
        - animal <- Sceneries with animals
        - empty  <- Sceneries without animals 
```
* With images in correct folders run:
```
python ./dataset_generator.py
```
* This will generate dataset like:
```
model_1st_stage
- dataset
    - processed
        - animal <- Sceneries with animals
        - empty  <- Sceneries without animals 
```
* Now you can clone my [Edge Impulse model](https://studio.edgeimpulse.com/public/780187/live) and tune it to your dataset
* After training through Edge Impulse replace animal_classifier/mcu/lib/animal-binary-classifier.zip with your version and rebuild mcu firmware