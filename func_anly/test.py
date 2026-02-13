import csv
import json

with open("result/resource_anly/resource_anly_result.json", "r", encoding="utf-8") as f:
  data = json.load(f)

with open("result/resource_anly/resource_anly_result.csv", "w", encoding="utf-8") as f:
  writer = csv.writer(f)
  writer.writerow(["ID", "项目名", "父子关系数"])
  for index, (project_name, r) in enumerate(data.items()):
    writer.writerow([index, project_name, r["has_relationship"]])
