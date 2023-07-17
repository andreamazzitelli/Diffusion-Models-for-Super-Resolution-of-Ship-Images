import fiftyone as fo
from fiftyone import ViewField as F
import pandas as pd
from math import ceil
import matplotlib.pyplot as plt
import tqdm
import random
import seaborn as sns

ship_categories = []
categories_view = []
output_size = 500000

with open("File Containing in each line the name of the category") as File:
    for line in File:
        ship_categories.append(line.strip())

sample_per_category = ceil(output_size / len(ship_categories))
original_sample_per_category = sample_per_category

dataset = fo.load_dataset("DATASET_NAME")

for category in tqdm.tqdm(sorted(ship_categories)):
    
    view = dataset.load_saved_view(f"{category}_filtered") # views are precomputed to save time, for each category there is a view already filtered
    paths = [sample["filepath"] for sample in view]

    
    data_frame = pd.DataFrame({
        "filepath": paths,
        "category": [category for _ in range(len(paths))]
    })
    
    categories_view.append([data_frame, len(view)])

sorted_views = sorted(categories_view, key=lambda x : x[1])

final_df = pd.DataFrame(columns=["filepath"])

sample_distribution = []

for index, el in tqdm.tqdm(enumerate(sorted_views)):

    category = el[0].iloc[0]['category']

    if el[1] <= sample_per_category:

        final_df = pd.concat([final_df, el[0]], ignore_index=True)
        sample_per_category += ceil((sample_per_category - el[1])/len(sorted_views[index:]))
        sample_distribution.append([category, el[1]])

    else:
        
        sample = el[0].sample(n=sample_per_category)
        final_df = pd.concat([final_df, sample], ignore_index=True)
        sample_distribution.append([category, sample_per_category])


final_df.drop_duplicates(inplace=True)
final_df = final_df.sample(frac=1)

final_df = final_df.drop('category', axis=1)
final_df.to_csv("output.csv", index=False)


# Computing and Saving the Bar Chart of the distribution of the images
cat = []
n_sample = []

sample_distribution = sorted(sample_distribution, key=lambda x : x[0])

for el in sample_distribution:
    cat.append(el[0])
    n_sample.append(el[1])

plt.figure(figsize=(40, 22.50))
sns.barplot(x=n_sample, y=cat)
plt.yticks(fontsize= 'small')
plt.ylabel('Categories')
plt.xlabel('N. of Samples')
plt.title('Number of Samples per Category')
plt.savefig("output_histo.png")



