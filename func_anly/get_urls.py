import csv
import json

file = "web_url_stars.json"
csv_file = "func_anly_result_web_v3.csv"


def read_and_parse_csv(file_path):
  project_names = []
  try:
    with open(file_path, "r", encoding="utf-8") as f:
      reader = csv.DictReader(f)
      for row in reader:
        project_names.append(row["项目名称"])
  except FileNotFoundError:
    print("错误：文件未找到")
  except KeyError as e:
    print(f"错误: CSV 表头不匹配，缺失字段: {e}")
  return project_names


project_names = read_and_parse_csv(csv_file)

with open(file, "r", encoding="utf-8") as f:
  targets = json.loads(f.read())

for t in targets:
  owner = t["owner"]
  repo = t["repo"]
  if f"{owner}_{repo}" in project_names:
    print(t["url"])
