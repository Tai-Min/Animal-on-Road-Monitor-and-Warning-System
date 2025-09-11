# Dataset
[GRAM Road-Traffic Monitoring](https://gram.web.uah.es/data/datasets/rtm/index.html) </br>
Download only Image sequences and unpack them into ./dataset/traffic_(01, 02, 03)/raw

# Generate depth map
* Run 
```
python run.py --encoder vitl --img-path ../dataset/traffic_01/raw --outdir ../dataset/traffic_01/depth --pred-only
```
* Repeat for other traffic_0n folders

# Generate training data
* Run inside this folder (where README is)
```
python ./dataset_generator.py
```

# Training
* You may edit training.py to utilize GPU
* Run
```
python ./training.py
```

# Export model

