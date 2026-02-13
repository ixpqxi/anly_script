import json
import os

import dotenv
from openai import OpenAI

dotenv.load_dotenv()


def get_batch_status(client: OpenAI, batch_id: str):
  """查询任务状态"""
  batch = client.batches.retrieve(batch_id=batch_id)
  return batch.status, batch.output_file_id, getattr(batch, 'error_file_id', None)


def download_file(client: OpenAI, file_id: str, save_path: str):
  """下载结果或错误文件"""
  content = client.files.content(file_id)
  content.write_to_file(save_path)


def main():
  client = OpenAI(
      api_key=os.getenv("DASHSCOPE_API_KEY"),
      base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
  )

  with open("result/batch_ids.json", "r", encoding="utf-8") as f:
    batch_ids = json.load(f)

  for batch_id in batch_ids:
    status, output_file_id, error_file_id = get_batch_status(client, batch_id)
    if status == "completed":
      output_file_path = f"result/resource_anly/result/{batch_id}.json"
      download_file(client, output_file_id, output_file_path)
      print(f"Batch job completed. Batch ID: {batch_id}")
    elif status in ["failed", "expired", "cancelled"]:
      print(f"Batch job failed. Batch ID: {batch_id}")


if __name__ == "__main__":
  main()
