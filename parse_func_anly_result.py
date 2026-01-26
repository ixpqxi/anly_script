import csv
import json
import os
from typing import Dict, List, Set

from pydantic import BaseModel, Field, computed_field


class Operation(BaseModel):
  operation_type: str
  resource_objects: List[str]


class ResourceAnalysis(BaseModel):
  reason: str
  is_resource_operation: bool
  confidence: str
  operations: List[Operation]

#### result ####


class ResourceDetail(BaseModel):
  # 资源种类数量
  category: int = 0
  # 具体的资源名称及其操作集合: {"User": {"Read", "Update"}}
  resource_name: Dict[str, Set[str]] = Field(default_factory=dict)


class StatisticsResult(BaseModel):
  # 总接口数/调用数
  endpoint: int = 0
  # 涉及资源操作的接口数
  resource_operation_endpoint: int = 0
  # 资源详情
  resource: ResourceDetail = Field(default_factory=ResourceDetail)
  # 资源操作总次数
  resource_operation_num: int = 0

  # 平均值：resource_operation_num / resource_operation_endpoint
  @computed_field
  @property
  def avg_each_endpoint_resource_operation_num(self) -> float:
    if self.resource_operation_endpoint > 0:
      return round(self.resource_operation_num / self.resource_operation_endpoint, 2)
    else:
      return 0.0

  # 平均值：resource_operation_num / resource.category
  @computed_field
  @property
  def avg_each_resource_operation_endpoint(self) -> float:
    if self.resource.category > 0:
      return round(self.resource_operation_num / self.resource.category, 2)
    else:
      return 0.0


index_table = {}
result: Dict[str, StatisticsResult] = {}


def parse_single_result(obj: str):
  global result
  global index_table

  custom_id = obj["custom_id"]
  message = obj["response"]["body"]["choices"][0]["message"]

  project_name = index_table[int(custom_id)]
  if project_name not in result:
    result[project_name] = StatisticsResult()

  content = ResourceAnalysis.model_validate_json(message["content"])
  result[project_name].endpoint += 1
  if content.is_resource_operation:
    # if project_name == "yewstack_yew":
    #   print(content.model_dump_json())
    result[project_name].resource_operation_endpoint += 1
    for operation in content.operations:
      result[project_name].resource_operation_num += len(
          operation.resource_objects)
      for resource in operation.resource_objects:
        if resource not in result[project_name].resource.resource_name:
          result[project_name].resource.resource_name[resource] = set()
          result[project_name].resource.category += 1
        result[project_name].resource.resource_name[resource].add(
            operation.operation_type)


def parse_result_file(file_path):
  with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      parse_single_result(json.loads(line))


def load_index_table(file_path):
  global index_table

  with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      index_obj = json.loads(line)
      project_name = index_obj["target"].split(':')[0]
      index_table[index_obj["custom_id"]] = project_name


def print_table():
  res = ""

  '''
  打印结果数据表格

  表格格式为：

  | ID | 项目名称 | 总函数数量 | 资源种类数量 | 涉及资源操作的端点数 | 资源操作总数 | 资源操作总数/资源操作接口数 |
  | --- | --- | --- | --- | --- | --- | --- |
  | index | project_name | endpoint | resource.category | resource_operation_endpoint | resource_operation_num | avg_each_endpoint_resource_operation_num |
  '''
  res += "| ID | 项目名称 | 总函数数量 | 资源种类数量 | 涉及资源操作的端点数 | 资源操作总数 | 资源操作总数/资源操作接口数 |\n"
  res += "| --- | --- | --- | --- | --- | --- | --- |\n"
  for index, (project_name, r) in enumerate(result.items()):
    res += f"| {index} | {project_name} | {r.endpoint} | {r.resource.category} | {r.resource_operation_endpoint} | {r.resource_operation_num} | {r.avg_each_endpoint_resource_operation_num} |\n"
  return res


def print_target_table(target_project: str):
  for index, (project_name, r) in enumerate(result.items()):
    if project_name == target_project:
      print(f"| {index} | {project_name} | {r.endpoint} | {r.resource.category} | {r.resource_operation_endpoint} | {r.resource_operation_num} | {r.avg_each_endpoint_resource_operation_num} | {r.avg_each_resource_operation_endpoint} |")
      print(r.resource.resource_name)


def print_resource_name():
  for project_name, r in result.items():
    with open(f"result/resource/resource_name_{project_name}.txt", "w", encoding="utf-8") as f:
      for resource in r.resource.resource_name:
        f.write(resource + "\n")


def save_to_csv(file_path):
  with open(file_path, "w", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "项目名称", "总函数数量", "资源种类数量", "涉及资源操作的端点数",
                    "资源操作总数", "资源操作总数/资源操作接口数", "资源操作总数/资源种类数量"])
    for index, (project_name, r) in enumerate(result.items()):
      writer.writerow([index+97, project_name, r.endpoint, r.resource.category, r.resource_operation_endpoint,
                      r.resource_operation_num, r.avg_each_endpoint_resource_operation_num, r.avg_each_resource_operation_endpoint])


if __name__ == "__main__":
  betch_input_file = os.getenv("BETCH_INPUT_FILE")
  index_table_file = os.getenv("OUTPUT_INDEX_TABLE_FILE")

  load_index_table(index_table_file)

  parse_result_file(betch_input_file)
  # print_resource_name()
  # print(print_target_table("yewstack_yew"))
  save_to_csv("result/func_anly_result_web_2.csv")
  # with open("result/func_anly_result.md", "w", encoding="utf-8") as f:
  #   f.write(print_table())
  #   f.write(print_table())
  #   f.write(print_table())
