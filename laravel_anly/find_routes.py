import json
import os
import re


def find_route_files(directory, exclude_dirs=None):
  """
  递归查找 PHP 路由文件，并排除指定的目录。
  """
  if exclude_dirs is None:
    exclude_dirs = {'vendor', 'node_modules',
                    'storage', 'bootstrap', '.git', '.idea', 'tests'}
  else:
    exclude_dirs = set(exclude_dirs)

  for root, dirs, files in os.walk(directory):
    # 原地修改 dirs，过滤不需要进入的目录
    dirs[:] = [d for d in dirs if d not in exclude_dirs]

    for file in files:
      # if file.endswith('.php') and ('routes' in file.lower() or 'route' in file.lower()):
      if file.endswith('.php') and ('routes' in file.lower()):
        yield os.path.join(root, file)


def get_route_statements(text):
  """
  词法分析器（Tokenizer Lite）：
  从文本中安全地提取出每一个完整的 `Route::...;` 语句。
  完美处理多行闭包、数组嵌套、字符串内含分号等复杂情况。
  """
  statements = []
  idx = 0
  while True:
    idx = text.find("Route::", idx)
    if idx == -1:
      break

    stmt_start = idx
    curr = idx
    in_string = False
    string_char = ''
    brace_level = 0  # {} 层级
    paren_level = 0  # () 层级
    array_level = 0  # [] 层级

    while curr < len(text):
      char = text[curr]

      if not in_string:
        if char in ("'", '"'):
          in_string = True
          string_char = char
        elif char == '{':
          brace_level += 1
        elif char == '}':
          brace_level -= 1
        elif char == '(':
          paren_level += 1
        elif char == ')':
          paren_level -= 1
        elif char == '[':
          array_level += 1
        elif char == ']':
          array_level -= 1
        elif char == ';':
          # 当遇到分号，且所有的括号都已经闭合时，说明这是一个完整的语句
          if brace_level == 0 and paren_level == 0 and array_level == 0:
            statements.append(text[stmt_start:curr+1])
            idx = curr + 1
            break
      else:
        if char == '\\':
          curr += 1  # 跳过转义字符
        elif char == string_char:
          in_string = False

      curr += 1

    # 如果文件结尾都没遇到完整闭合的语句，直接跳出防止死循环
    if curr >= len(text):
      break

  return statements


def parse_blocks(text, current_prefix='', current_name='', current_middleware=None):
  """
  递归解析完整的路由语句列表
  """
  if current_middleware is None:
    current_middleware = []

  routes = []
  statements = get_route_statements(text)

  for stmt in statements:
    # 1. 检查是否是路由组 (Route Group)
    # 匹配 Route::...->group(function() { ... });
    group_match = re.search(
        r"^(Route\s*::.*?)(?:->\s*group\s*\(\s*function\s*\([^)]*\)\s*\{)(.*)\}\s*\)\s*;\s*$", stmt, flags=re.DOTALL | re.IGNORECASE)

    if group_match:
      # 例如: Route::prefix('vendor')->name('vendor.')->middleware($vendorMiddleware)
      chain_str = group_match.group(1)
      body = group_match.group(2)      # 闭包内部的代码块

      # 解析组属性: prefix
      prefix_match = re.search(
          r"->\s*prefix\s*\(\s*(['\"])(.*?)\1\s*\)", chain_str)
      g_prefix = prefix_match.group(2) if prefix_match else ''

      # 解析组属性: name
      name_match = re.search(
          r"->\s*name\s*\(\s*(['\"])(.*?)\1\s*\)", chain_str)
      g_name = name_match.group(2) if name_match else ''

      # 解析组属性: middleware (支持提取字符串或变量，如 $vendorMiddleware)
      g_middleware = []
      mid_match = re.search(
          r"->\s*middleware\s*\(\s*(.*?)\s*\)", chain_str, flags=re.DOTALL)
      if mid_match:
        m_str = mid_match.group(1)
        items = re.findall(r"['\"](.*?)['\"]|\$([a-zA-Z0-9_]+)", m_str)
        for item in items:
          val = item[0] if item[0] else '$' + item[1]
          if val:
            g_middleware.append(val)

      # 合并当前上下文和组的新属性
      new_prefix = (current_prefix + '/' +
                    g_prefix).strip('/') if g_prefix else current_prefix
      new_name = current_name + g_name
      new_middleware = current_middleware + g_middleware

      # 递归解析组内的代码
      routes.extend(parse_blocks(body, new_prefix, new_name, new_middleware))
      continue

    # 2. 检查是否是重定向路由 (Route::redirect)
    redirect_match = re.search(
        r"Route\s*::\s*redirect\s*\(\s*(['\"])(.*?)\1\s*,\s*(['\"])(.*?)\3", stmt, flags=re.DOTALL | re.IGNORECASE)
    if redirect_match:
      uri = redirect_match.group(2)
      dest = redirect_match.group(4)
      full_uri = (current_prefix + '/' + uri).strip('/')
      routes.append({
          'method': 'REDIRECT',
          'uri': full_uri,
          'action': f"Redirect to -> {dest}",
          'name': current_name if current_name else None,
          'middleware': current_middleware
      })
      continue

    # 3. 解析标准 HTTP 请求路由 (Route::get, post, put, etc.)
    verb_match = re.search(
        r"Route\s*::\s*(get|post|put|patch|delete|any|options)\s*\(\s*(['\"])(.*?)\2\s*,\s*(.*?)\s*\)(?:\s*->|;|$)", stmt, flags=re.DOTALL | re.IGNORECASE)
    if verb_match:
      method = verb_match.group(1).upper()
      uri = verb_match.group(3)
      action = verb_match.group(4).strip()

      # 清除 action 末尾可能出现的逗号 (如数组后的拖尾逗号)
      if action.endswith(','):
        action = action[:-1].strip()
      # 压缩多行 action 中的空格和换行符，使其适合单行显示
      action = re.sub(r"\s+", " ", action)

      full_uri = (current_prefix + '/' + uri).strip('/')

      # 提取挂载在该路由上的局部 Name
      name_match = re.search(r"->\s*name\s*\(\s*(['\"])(.*?)\1\s*\)", stmt)
      local_name = name_match.group(2) if name_match else ''
      full_name = current_name + \
          local_name if (current_name or local_name) else None

      # 提取挂载在该路由上的局部 Middleware
      local_middleware = []
      mid_match = re.search(
          r"->\s*middleware\s*\(\s*(.*?)\s*\)(?:\s*->|;|$)", stmt, flags=re.DOTALL)
      if mid_match:
        m_str = mid_match.group(1)
        items = re.findall(r"['\"](.*?)['\"]|\$([a-zA-Z0-9_]+)", m_str)
        for item in items:
          val = item[0] if item[0] else '$' + item[1]
          if val:
            local_middleware.append(val)

      full_middleware = current_middleware + local_middleware

      routes.append({
          'method': method,
          'uri': full_uri,
          'action': action,
          'name': full_name,
          'middleware': full_middleware
      })

  return routes


def to_json(routes):
  content = json.dumps(routes, indent=2, ensure_ascii=False)
  with open("result/laravel_anly/un_auth_routes.json", "w", encoding="utf-8") as f:
    f.write(content)
  return content


def main():
  project_root = '/root/code/py/anly_script/laravel_anly/'

  route_files_found = False

  print(f"开始扫描目录: {os.path.abspath(project_root)}")

  for file_path in find_route_files(project_root):
    try:
      with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

      routes = parse_blocks(content)
      print(to_json(routes))
      # if routes:
      #   route_files_found = True
      #   print(f"\n[{file_path}]")
      #   for route in routes:
      #     print(f"  [{route['method']}] {route['uri']}")
      #     print(f"      Action: {route['action']}")
      #     if route['name']:
      #       print(f"      Name  : {route['name']}")
      #     if route['middleware']:
      #       print(f"      Middle: {', '.join(route['middleware'])}")
    except Exception as e:
      print(f"解析文件出错 {file_path}: {e}")

  if not route_files_found:
    print("未提取到任何路由，请检查项目路径是否正确。")


if __name__ == "__main__":
  main()
