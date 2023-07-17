import fiftyone as fo
import fiftyone.brain as fob
import fiftyone.zoo as foz
print("Loading Dataset")
dataset = fo.load_dataset("ship_dataset")
print("Dataset Loaded")

fob.compute_visualization(
    dataset,
    embeddings= "embedding",
    num_dims=2,
    method="umap",
    brain_key="umap_visualization_50_neighbors",
    verbose=True,
    seed=16,
    num_neighbors=50
)



fob.compute_similarity(    
    dataset,
    embeddings= "embedding",
    brain_key="similarity"
)
fob.compute_uniqueness(
    dataset,
    embeddings= "embedding"
)

model = foz.load_zoo_model("resnet50-imagenet-torch")
embeddings = dataset.compute_embeddings(model, embeddings_field="embedding", num_workers=8)