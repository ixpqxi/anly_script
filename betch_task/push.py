import json
import os
from pathlib import Path

import dotenv
from openai import OpenAI

dotenv.load_dotenv()


def create_batch_job(client: OpenAI, input_file: str, endpoint: str = "/v1/chat/completions") -> str:
  file_object = client.files.create(file=Path(input_file), purpose="batch")
  input_file_id = file_object.id
  print(f"Input file uploaded. File ID: {input_file_id}")
  """创建批量任务，返回 batch_id"""
  batch = client.batches.create(
      input_file_id=input_file_id,
      endpoint=endpoint,
      completion_window="24h"
  )
  return batch.id


def main():
  client = OpenAI(
      api_key=os.getenv("DASHSCOPE_API_KEY"),
      base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
  )

  betch_ids = []

  betch_input_dir = r"./result/resource_anly/"
  files = os.listdir(betch_input_dir)
  for file in files:
    file_path = os.path.join(betch_input_dir, file)
    batch_id = create_batch_job(client, file_path)
    print(f"Batch job created. Batch ID: {batch_id}")
    betch_ids.append(batch_id)
    print("File: ", file_path)

  with open("result/batch_ids.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(betch_ids))


if __name__ == "__main__":
  main()
