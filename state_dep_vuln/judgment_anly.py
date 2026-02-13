import json
import os
import sys

import dotenv
from json_repair import repair_json
from openai import OpenAI
from tqdm import tqdm

dotenv.load_dotenv()

DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")
DEEPSEEK_URL = os.getenv("DEEPSEEK_URL")
model = os.getenv("MODEL")


def read_file(file: str):
  with open(file, "r", encoding="utf-8") as f:
    return f.read()


def write_file(file: str, content: str):
  with open(file, "w", encoding="utf-8") as f:
    f.write(content)


prompt = read_file("./state_dep_vuln/prompts/judgment.md")

client = OpenAI(
    api_key=DEEPSEEK_KEY,
    base_url=DEEPSEEK_URL,
)


def analyze_report(report_text):

  content = prompt.replace("{{REPORT_CONTENT_HERE}}", report_text)

  response = client.chat.completions.create(
      model=model,  # 建议使用 GPT-4 或 Claude 3.5 Sonnet 以获得最佳逻辑理解
      messages=[{"role": "user", "content": content}],
      temperature=0.1
  )

  try:
    result = repair_json(response.choices[0].message.content)
    return json.loads(result)
  except json.JSONDecodeError:
    return {"error": "Invalid JSON"}


def get_report_paths(main_dir: str):
  report_paths = [os.path.join(main_dir, file, ghsa, f"{ghsa}.json") for file in os.listdir(
      main_dir) for ghsa in os.listdir(os.path.join(main_dir, file))]
  write_file("./tmp/report_paths.json", json.dumps(report_paths))

# 示例调用
# report = "Title: IDOR in delete comment... Steps: 1. Login... 2. Get comment_id..."
# result = analyze_report(report)
# print(result)


def main(start: int, end: int):
  report_paths_raw = read_file("./tmp/report_paths.json")
  report_paths = json.loads(report_paths_raw)
  print("报告总数:", len(report_paths))
  print("报告范围:", start, end)

  if end == "-1":
    reports = report_paths[start:]
  else:
    reports = report_paths[start:end]

  with open("result/state_dep_vuln/judgment_result_4.jsonl", "a", encoding="utf-8") as f:
    for report_path in tqdm(reports, desc="正在分析报告", unit="report"):
      report_raw = read_file(report_path)
      report = json.loads(report_raw)

      if "details" not in report:
        continue
      details = report["details"]
      if len(details) < 500:
        continue

      result = analyze_report(details)
      result["report_path"] = report_path
      f.write(json.dumps(result) + "\n")


if __name__ == "__main__":
  start = int(sys.argv[1])
  end = int(sys.argv[2])

  main(start, end)
