import json
import os
from typing import Dict

from json_repair import repair_json
from pydantic import BaseModel, Field


class ResourceRelationship(BaseModel):
  reason: str
  has_relationship: bool
  parent: str = None
  child: str = None


class StatisticsResult(BaseModel):
  has_relationship: int = 0
  relationship: Dict[str, set] = Field(default_factory=dict)


index_table = {}
result: Dict[str, StatisticsResult] = {}


def parse_single_result(obj: str):
  global result

  custom_id = obj["custom_id"]
  message = obj["response"]["body"]["choices"][0]["message"]

  project_name = index_table[int(custom_id)]
  if project_name not in result:
    result[project_name] = StatisticsResult()

  try:
    content = ResourceRelationship.model_validate_json(
        repair_json(message["content"]))
  except Exception as e:
    return

  if content.has_relationship:
    result[project_name].has_relationship += 1
    if content.parent not in result[project_name].relationship:
      result[project_name].relationship[content.parent] = set()
    result[project_name].relationship[content.parent].add(content.child)


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


def save_to_json(file: str, result: Dict[str, StatisticsResult]):
  serializable_result = {}
  for k, v in result.items():
    data = v.model_dump()
    # 将 relationship 里的所有 set 值转为 list
    data['relationship'] = {
        rel_k: list(rel_v) if isinstance(rel_v, set) else rel_v
        for rel_k, rel_v in data['relationship'].items()
    }
    serializable_result[k] = data
  with open(file, "w", encoding="utf-8") as f:
    json.dump(serializable_result, f, ensure_ascii=False, indent=2)


def parse():
  r = "./result/resource_anly/result"
  files = os.listdir(r)
  for file in files:
    file_path = os.path.join(r, file)
    print("="*20)
    print(file_path)
    parse_result_file(file_path)


if __name__ == "__main__":
  index_table_file = r"./result/index_table/resource_index_table.jsonl"

  load_index_table(index_table_file)

  parse()

  save_to_json("result/resource_anly/resource_anly_result.jsonl", result)
