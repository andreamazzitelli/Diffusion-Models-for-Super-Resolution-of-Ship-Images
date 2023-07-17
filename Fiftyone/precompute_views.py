import fiftyone as fo
from fiftyone import ViewField as F

print("Loading Dataset")
dataset = fo.load_dataset("ship_dataset")
print("Dataset Loaded")


with open("/home/andrea/Desktop/andream/categories.txt") as File:
    for category in File:
        category = category.strip()
        
        view = dataset.match(F("ship_category").contains_str(category))
        dataset.save_view(category, view, description=f"View containing all ship of category {category}" )