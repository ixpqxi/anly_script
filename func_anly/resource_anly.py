import json
import os


def read_file(file_path):
  """Reads the content of a file and returns it as a string."""
  with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()
  return content


def single_input(
    custom_id: int,
    prompt: str,
    resource_a: str,
    resource_b: str
):

  content = prompt.format(
      resource_a=resource_a,
      resource_b=resource_b
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
  resource_data_dir = r"./result/resource_name_web/"
  output_index_table_file = r"./result/index_table/resource_index_table.jsonl"
  project_files = os.listdir(resource_data_dir)

  prompt = read_file(r"./prompts/resource_anly.md")
  batch_size = 45000
  custom_id = 0
  batch_num = 0
  batch_f = None  # 用于持有当前批处理文件的句柄

  project_num = 0
  try:
    with open(output_index_table_file, "a", encoding="utf-8") as itf:
      for file in project_files:
        project_file_path = os.path.join(resource_data_dir, file)
        project_base_name = file.replace('.json', '')
        print(project_num, project_file_path)
        project_num += 1
        data = json.loads(read_file(project_file_path))

        # 梯型
        for i, r_i in enumerate(data):
          for j, r_j in enumerate(data):
            if j < i:
              if custom_id % batch_size == 0:
                if batch_f:
                  batch_f.close()
                batch_num += 1
                batch_file_path = f"result/resource_anly/batch_inputs_file_{batch_num}.jsonl"
                batch_f = open(batch_file_path, "a", encoding="utf-8")

                # 生成输入数据
              input_data = single_input(custom_id, prompt, r_i, r_j)

              # 写入批处理文件（利用已打开的句柄）
              batch_f.write(json.dumps(
                  input_data, ensure_ascii=False) + "\n")

              target = f"{project_base_name}:{r_i}:{r_j}"
              itf.write(json.dumps(
                  {"custom_id": custom_id, "target": target}) + "\n")

              custom_id += 1
  finally:
    if batch_f:
      batch_f.close()


if __name__ == "__main__":
  gen_batch_inputs()

# files = os.listdir("result/resource_name_cicd")

# for file in files[:1]:
#   file_path = os.path.join("result/resource_name_cicd", file)
#   with open(file_path, "r", encoding="utf-8") as f:
#     data = json.load(f)
#     single_file(data)
