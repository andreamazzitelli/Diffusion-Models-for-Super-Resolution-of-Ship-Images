import pandas as pd
import fiftyone as fo
import tqdm

print("Loading Fiftyone Dataset and CleanVision Report")
report = pd.read_csv("Path to ClenaVisionReport")
dataset = fo.load_dataset("DATASET_NAME")
print("Done Loading")

for _, row in tqdm.tqdm(report.iterrows()):
        
    path = row[0]
    temp = fo.Sample(filepath=path)

    sample = dataset[temp.filepath]

    for col_name, col_value in row.items():
            
        if col_name == "Unnamed: 0":
            continue
            
        elif col_name == "odd_aspect_ratio_score" or col_name == "low_information_score" or col_name == "light_score" or col_name == "dark_score" or col_name == "blurry_score":
            sample[col_name] = col_value
            
        elif col_name == "is_odd_aspect_ratio_issue" and col_value:
            sample.tags.append("odd_aspect_ratio")

        elif col_name == "is_low_information_issue" and col_value:
            sample.tags.append("low_information")

        elif col_name == "is_light_issue" and col_value:
            sample.tags.append("overexposed")

        elif col_name == "is_dark_issue" and col_value:
            sample.tags.append("underexposed")

        elif col_name == "is_blurry_issue" and col_value:
            sample.tags.append("blurry")

        elif col_name == "is_exact_duplicates_issue" and col_value:
            sample.tags.append("exact_duplicate")

        elif col_name == "is_near_duplicates_issue" and col_value:
            sample.tags.append("near_duplicate")
  
    sample.save()
