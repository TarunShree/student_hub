import pandas as pd

from recommender.preprocessing import prepare_project


projects = pd.read_csv("data/projects.csv")

project = projects.iloc[0].to_dict()

result = prepare_project(project)

print(result)