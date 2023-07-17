import fiftyone.brain as fob
import fiftyone as fo
import cv2
import numpy as np
import pandas as pd
import glob
import json
import tqdm
import re

# The dataset should have the following structure.
# root
# |- category_1
# |  |-image1.jpg
# |  |-image2.jpg
# |  |-metadata.csv
# |
# |- category_2
# |-category_3

dataset_dir = "Root to images"

dataset = fo.Dataset("DATASET_NAME")
dataset.persistent = True

for up_path in glob.glob(dataset_dir): # Loading one Subfolder at the time

    samples = []

    # Reading metadata file
    metadata_file = f"{up_path}/metadata.csv"
    metadata = pd.read_csv(metadata_file, index_col=0) 
    
    up_path = f"{up_path}/*.jpg"
    for file_path in tqdm.tqdm(glob.glob(up_path)): # Loading one image in the subfolder at the time 
        
        
        sample = fo.Sample(filepath=file_path)

        id = file_path.split("/")[-1].split(".")[0]
        sample['image_id'] = id

        try:
            line = metadata.loc[int(id)] # getting row relative to the id

            # Adding Fields to Sample 
            for col_name in line.axes[0]:
                sample[col_name] = str(line[col_name])

        except KeyError:
            
            print(f"{up_path} - Cannot find row with associated id {id}")
            with open("./fifty.log", "a") as logFile:
                logFile.write(f"{up_path} - Cannot find row with associated id {id}\n")

        samples.append(sample)

    dataset.add_samples(samples) # adding subfolder to the dataset

dataset.compute_metadata() # computing standard photo metadata

# session = fo.launch_app(dataset, remote=True)
# session.wait()
