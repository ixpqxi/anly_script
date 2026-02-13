import json
import os

from dotenv import load_dotenv

load_dotenv()


def read_file(file_path):
  """Reads the content of a file and returns it as a string."""
  with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()
  return content


def save_data(file: str, input_data: dict):
  with open(file, "a+", encoding="utf-8") as f:
    f.write(json.dumps(input_data) + "\n")


def single_input(
    custom_id: int,
    prompt: str,
    function_definition: str
):

  content = prompt.format(
      function_definition=function_definition
  )

  input_data = {
      "custom_id": f"{custom_id}",
      "method": "POST",
      "url": "/v1/chat/completions",
      "body": {
          "model": "qwen3-max",
          "messages": [
              {"role": "user", "content": content}
          ]
      },
      "response_format": {"type": "json_object"},
      "temperature": 0.1
  }

  return input_data


def gen_batch_inputs():
  func_data_dir = os.getenv(
      "FUNC_DATA_DIR", "")
  output_index_table_file = os.getenv(
      "OUTPUT_INDEX_TABLE_FILE", "result/index_table.json")
  project_files = os.listdir(func_data_dir)

  prompt = read_file(os.getenv("PROMPT_FILE"))
  code_snippets_hashes = set()

  batch_size = 45000
  i = 0
  batch_num = 1
  batch_f = None  # 用于持有当前批处理文件的句柄

  j = 0
  try:
    with open(output_index_table_file, "a", encoding="utf-8") as itf:
      for file in project_files:
        project_file_path = os.path.join(func_data_dir, file)
        project_base_name = file.replace('.json', '')
        print(j, project_file_path)
        j += 1
        data = json.loads(read_file(project_file_path))

        for file_name, func_list in data.items():
          if func_list is None or len(func_list) == 0:
            continue
          for idx, func_def in enumerate(func_list):
            function_hash = hash(func_def)

            if function_hash in code_snippets_hashes:
              continue

            # 检查是否需要切换批处理文件
            if i % batch_size == 0:
              if batch_f:
                batch_f.close()
              batch_num += 1
              batch_file_path = f"result/batch_inputs_file_{batch_num}.jsonl"
              batch_f = open(batch_file_path, "a", encoding="utf-8")

            # 生成输入数据
            input_data = single_input(i, prompt, func_def)

            # 写入批处理文件（利用已打开的句柄）
            batch_f.write(json.dumps(input_data, ensure_ascii=False) + "\n")

            # 更新哈希集和索引表
            code_snippets_hashes.add(function_hash)
            target = f"{project_base_name}:{file_name}:{idx}"
            itf.write(json.dumps({"custom_id": i, "target": target}) + "\n")

            i += 1
  finally:
    if batch_f:
      batch_f.close()


if __name__ == "__main__":
  gen_batch_inputs()
