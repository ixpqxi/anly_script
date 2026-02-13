"""
资源分析结果统计脚本
"""

import csv
import json
import statistics


def read_csv_file(file_path):
  data = []
  with open(file_path, 'r', newline='') as file:
    reader = csv.reader(file)
    for row in reader:
      data.append(row)
  return data[1:]


with open("result/web_url_stars.json", "r", encoding="utf-8") as f:
  web_urls = json.load(f)


def save_csv_file(data, file_path):
  with open(file_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "项目名", "资源种类数量", "父子关系数",
                    "父子关系数/最大父子关系数(最坏情况)", "stars", "status"])
    for index, (project_name, r) in enumerate(data.items()):
      writer.writerow([index, project_name, r["resource_num"],
                      r["has_relationship"], r["rate"], r["stars"], r["status"]])


data = read_csv_file('result/resource_anly/resource_anly_result.csv')

result = {}

num_max = 0
num_max_project = ""
rate_max = 0.0
rate_max_project = ""

exclude_project = {}
project_num = len(data)

# 记录父子关系数总和
relationship_num = 0
# --- 新增：用于存储所有有效数值以计算中位数 ---
valid_nums = []

for i in data:
  info = {}
  project_name = i[1]

  if project_name not in ["yacy_yacy_search_server"]:
    owner, repo = project_name.split('_')
  else:
    owner = "yacy"
    repo = "yacy_search_server"

  for web_url in web_urls:
    if web_url["owner"] == owner and web_url["repo"] == repo:
      info["stars"] = web_url["stars"]
      break

  with open("./result/resource_name_web/" + project_name + ".json", "r", encoding="utf-8") as f:
    resource_data = json.load(f)
  num = len(resource_data)
  print("*"*10)
  print("Project:", project_name, "Num:", num)

  info["resource_num"] = num

  anlyed_resource_num = int(i[2])
  info["has_relationship"] = anlyed_resource_num
  if anlyed_resource_num > 68709 or ((num * num) / 2) <= 0 or num == 0:
    info["status"] = "excluded"
    exclude_project[project_name] = info["stars"]
    info["rate"] = round(anlyed_resource_num / ((num * num) / 2), 2)
    continue
  else:
    info["status"] = ""
    info["rate"] = round(anlyed_resource_num / ((num * num) / 2), 2)

  if (info["rate"] == 0 or info["rate"] > 1):
    info["status"] = "excluded"
    exclude_project[project_name] = info["stars"]
    continue

  relationship_num += anlyed_resource_num
  valid_nums.append(anlyed_resource_num)

  if anlyed_resource_num > num_max:
    num_max = anlyed_resource_num
    num_max_project = project_name

  if info["rate"] > rate_max:
    rate_max = info["rate"]
    rate_max_project = project_name

  result[project_name] = info

if valid_nums:
  median_val = statistics.median(valid_nums)
else:
  median_val = 0


save_csv_file(result, 'result/resource_anly/resource_anly_result_v3.csv')
print("exclude_project:", exclude_project)
print("父子关系数最大值:", num_max)
print("父子关系数最大值项目:", num_max_project)
print("="*10)
print("父子关系数/最大父子关系数最大值:", rate_max)
print("父子关系数/最大父子关系数最大值项目:", rate_max_project)
print("="*10)
print("父子关系数总和:", relationship_num)
print("父子关系数平均数:", round(relationship_num /
      (project_num - len(exclude_project)), 2))
print("="*10)
# --- 输出中位数 ---
print("父子关系数中位数:", median_val)
print("="*10)

print("===== 未排除的项目 =====")
print("项目数：", len(result))
print(list(result.keys()))
