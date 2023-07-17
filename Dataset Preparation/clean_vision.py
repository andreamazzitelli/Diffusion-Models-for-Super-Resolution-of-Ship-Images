from cleanvision.imagelab import Imagelab

imagelab = Imagelab(data_path="Dataset Root")
imagelab.find_issues()
imagelab.issues.to_csv("Path where to store report")