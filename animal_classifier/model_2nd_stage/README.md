# Introduction
This part of the project is used to generate model for second stage animal detection.

# Dataset
[Animal Image Dataset (90 Different Animals)](https://www.kaggle.com/datasets/iamsouravbanerjee/animal-image-dataset-90-different-animals) </br>
Keep only folders specified in project_config.py's ANIMAL_SECOND_STAGE_TYPES and unpack them to ./dataset/animals

# Generate training data
* Inside this directory run:
```
python ./dataset_generator.py
```

# Training
* You may edit training.py to utilize GPU
* Run:
```
python ./training.py
```

# Export model
* Run:
```
python ./export.py
```

Now model should be placed inside the correct folder in runtime script.