import pandas as pd
import os
import shutil
import tqdm

dataframe = pd.read_csv("Path to Subset csv file")

# The split of the subset of the dataset in train set, validation set and test set considering the variables train_size and val_size 
# and the length of the dataframe "dataframe" is as follows:
#
# train_set_size = len(dataframe) * train_size
# validation_set_set = (len(dataframe) - train_len) * val_size
# test_set_size = len(dataframe) - train_len - val_size


train_size = 1. 
val_size = 0. 

destination_path = "Folder where to copy"

train_path = os.path.join(destination_path, "train")
val_path = os.path.join(destination_path, "val")
test_path = os.path.join(destination_path, "test")

if not os.path.exists(destination_path):
    os.makedirs(destination_path)
    os.mkdir(train_path)
    os.mkdir(val_path)
    os.mkdir(test_path)
else:
    assert os.path.isdir(destination_path)

    if os.path.exists(train_path) and os.path.isdir(train_path) :
        shutil.rmtree(train_path)
    os.mkdir(train_path)

    if os.path.exists(val_path) and os.path.isdir(val_path) :
        shutil.rmtree(val_path)
    os.mkdir(val_path)

    if os.path.exists(test_path) and os.path.isdir(test_path) :
        shutil.rmtree(test_path)
    os.mkdir(test_path)
    
   
train_len = int(len(dataframe) * train_size)
train_df = dataframe.head(train_len)

remaining =  len(dataframe) - train_len
remaining_df = dataframe.tail(remaining)

val_len = round(remaining * val_size)
val_df = remaining_df.head(val_len)

test_len = remaining - val_len
test_df = remaining_df.tail(test_len)

for _, row in tqdm.tqdm(train_df.iterrows()):
    source = row["filepath"]
    id = source.split("/")[-1]

    destination = os.path.join(train_path, id)
    shutil.copy(source, destination)

for _, row in tqdm.tqdm(val_df.iterrows()):
    source = row["filepath"]
    id = source.split("/")[-1]

    destination = os.path.join(val_path, id)
    shutil.copy(source, destination)

for _, row in tqdm.tqdm(test_df.iterrows()):
    source = row["filepath"]
    id = source.split("/")[-1]

    destination = os.path.join(test_path, id)
    shutil.copy(source, destination)

