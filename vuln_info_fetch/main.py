from typing import Any, Dict, Optional

import requests


def get_advisory_by_cve(cve_id: str) -> Optional[Dict[str, Any]]:
  """
  根据CVE ID查询安全公告信息

  Args:
      cve_id: CVE标识符,例如 "CVE-2023-12345"

  Returns:
      如果查询成功返回JSON数据(字典),失败返回None
  """
  # 构建URL
  url = f"http://192.168.209.42:3001/api/advisories?aliases={cve_id}"

  try:
    # 发送GET请求
    response = requests.get(url)

    # 处理响应内容
    if response.status_code == 200:
      data = response.json()
      # print(f"响应数据: {data}")
      return data
    else:
      print(f"查询失败: {response.text}")
      return None

  except requests.exceptions.ConnectionError:
    print("无法连接到服务器，请确保服务器正在运行")
    return None
  except requests.exceptions.RequestException as e:
    print(f"请求错误: {e}")
    return None
  except ValueError as e:
    print(f"JSON解析错误: {e}")
    return None


def query_advisory_by_ghsa(ghsa_id: str) -> Optional[Dict[str, Any]]:
  """
  根据GHSA ID查询安全公告信息

  Args:
      ghsa_id: GHSA标识符,例如 "GHSA-xxhx-7292-7rv8"

  Returns:
      如果查询成功返回JSON数据(字典),失败返回None
  """
  # 构建URL
  url = f"http://192.168.209.42:3001/api/advisories/{ghsa_id}"

  try:
    # 发送GET请求
    response = requests.get(url)

    # 打印响应状态码
    # print(f"状态码: {response.status_code}")

    # 处理响应内容
    if response.status_code == 200:
      # print(f"查询{ghsa_id}成功！")
      data = response.json()
      # print(f"响应数据: {data}")
      return data
    else:
      print(f"查询失败: {response.text}")
      return None

  except requests.exceptions.ConnectionError:
    print("无法连接到服务器，请确保服务器正在运行")
    return None
  except requests.exceptions.RequestException as e:
    print(f"请求错误: {e}")
    return None
  except ValueError as e:
    print(f"JSON解析错误: {e}")
    return None


# == == == == == == == == == == == == == == == == == == == == == == =
cve = "CVE-2015-2483"

cve_data = get_advisory_by_cve(cve)
if not cve_data.get("results"):
  print(f"Skipping {cve}: No advisory data found.")
  # continue

cve_info = cve_data.get("results", [])[0]
ghsa_id = cve_info.get("id")
advisory_info = query_advisory_by_ghsa(ghsa_id)
print(advisory_info)
