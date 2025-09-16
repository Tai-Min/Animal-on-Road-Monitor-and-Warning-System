# Introduction
This part of the project is used to generate model for camera based air visibility estimation.

# Dataset
[GRAM Road-Traffic Monitoring](https://gram.web.uah.es/data/datasets/rtm/index.html) </br>
Download only Image sequences and unpack them into ./dataset/traffic_(01, 02, 03)/raw

# Generate depth map
* Inside this directory run: 
```
python Depth-Anything/run.py --encoder vitl --img-path ../dataset/traffic_01/raw --outdir ../dataset/traffic_01/depth --pred-only
```
* Repeat for other traffic_0n folders, this will generate depth data required for dataset processing

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