import os
import re


def extract_routes(file_path):
  """
  Extracts route information from a PHP file containing Laravel route definitions.

  Args:
      file_path (str): The path to the PHP file.

  Returns:
      list: A list of dictionaries, where each dictionary represents a route
            and contains keys like 'method', 'uri', 'action', 'middleware', 'name', etc.
            Returns an empty list if no routes are found or if the file is invalid.
  """
  routes = []
  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      content = f.read()

    # Regular expressions to match different route definitions.  These are important.
    # Handle simple GET/POST/PUT/PATCH/DELETE routes
    simple_route_regex = re.compile(
        r"\bRoute::(get|post|put|patch|delete)\s*\(\s*['\"](.*?)['\"]\s*,\s*\[(.*?)\]\s*\)\s*;"
    )
    # Handle route with name
    named_route_regex = re.compile(
        r"\bRoute::(get|post|put|patch|delete)\s*\(\s*['\"](.*?)['\"]\s*,\s*\[(.*?)\]\s*\)\s*->name\s*\(\s*['\"](.*?)['\"]\s*\)\s*;"
    )
    # Handle route with middleware
    middleware_route_regex = re.compile(
        r"\bRoute::(get|post|put|patch|delete)\s*\(\s*['\"](.*?)['\"]\s*,\s*\[(.*?)\]\s*\)\s*->middleware\s*\(\s*\[(.*?)\]\s*\)\s*;"
    )
    # Handle route with name and middleware
    named_middleware_route_regex = re.compile(
        r"\bRoute::(get|post|put|patch|delete)\s*\(\s*['\"](.*?)['\"]\s*,\s*\[(.*?)\]\s*\)\s*->name\s*\(\s*['\"](.*?)['\"]\s*\)\s*->middleware\s*\(\s*\[(.*?)\]\s*\)\s*;"
    )
    # Handle route groups (prefix and middleware)
    route_group_regex = re.compile(
        # DOTALL to allow . to match newline
        r"\bRoute::prefix\s*\(\s*['\"](.*?)['\"]\s*\)\s*->name\s*\(\s*['\"](.*?)['\"]\s*\)\s*->middleware\s*\(\s*\[(.*?)\]\s*\)\s*->group\s*\(.*?{(.*?)}\s*\)\s*;", re.DOTALL)

    # Group processing
    for group_match in route_group_regex.finditer(content):
      prefix = group_match.group(1)
      group_name = group_match.group(2)
      group_middleware_str = group_match.group(3)
      group_routes_block = group_match.group(4)
      group_middleware = [m.strip(" '") for m in re.findall(
          # Extract middleware
          r"'([^']*)'", group_middleware_str)] if group_middleware_str else []

      # Now, extract individual routes *within* the group block
      # Named routes
      for route_match in re.finditer(r"\bRoute::(get|post|put|patch|delete)\s*\(\s*['\"](.*?)['\"]\s*,\s*\[(.*?)\]\s*\)\s*->name\s*\(\s*['\"](.*?)['\"]\s*\)\s*;", group_routes_block):
        method = route_match.group(1)
        # Correctly handle prefix
        uri = prefix + '/' + \
            route_match.group(2) if prefix else route_match.group(2)
        action = route_match.group(3).strip()
        # Correctly handle namespaced route names
        name = group_name + route_match.group(4)
        routes.append({
            'method': method,
            'uri': uri,
            'action': action,
            'middleware': group_middleware,
            'name': name
        })

      # Middleware routes
      for route_match in re.finditer(r"\bRoute::(get|post|put|patch|delete)\s*\(\s*['\"](.*?)['\"]\s*,\s*\[(.*?)\]\s*\)\s*->middleware\s*\(\s*\[(.*?)\]\s*\)\s*;", group_routes_block):
        method = route_match.group(1)
        uri = prefix + '/' + \
            route_match.group(2) if prefix else route_match.group(2)
        action = route_match.group(3).strip()
        middleware_str = route_match.group(4)
        middleware = [m.strip(" '") for m in re.findall(
            r"'([^']*)'", middleware_str)] if middleware_str else []
        routes.append({
            'method': method,
            'uri': uri,
            'action': action,
            # Combine group and route-specific middleware
            'middleware': group_middleware + middleware,
            'name': None
        })

      # Simple routes
      for route_match in re.finditer(r"\bRoute::(get|post|put|patch|delete)\s*\(\s*['\"](.*?)['\"]\s*,\s*\[(.*?)\]\s*\)\s*;", group_routes_block):
        method = route_match.group(1)
        uri = prefix + '/' + \
            route_match.group(2) if prefix else route_match.group(2)
        action = route_match.group(3).strip()
        routes.append({
            'method': method,
            'uri': uri,
            'action': action,
            'middleware': group_middleware,  # Use the group's middleware
            'name': None
        })

    # Simple routes outside groups
    for match in simple_route_regex.finditer(content):
      method = match.group(1)
      uri = match.group(2)
      action = match.group(3).strip()
      routes.append({
          'method': method,
          'uri': uri,
          'action': action,
          'middleware': [],
          'name': None
      })

    # Named routes outside groups
    for match in named_route_regex.finditer(content):
      method = match.group(1)
      uri = match.group(2)
      action = match.group(3).strip()
      name = match.group(4)
      routes.append({
          'method': method,
          'uri': uri,
          'action': action,
          'middleware': [],
          'name': name
      })

    # Middleware routes outside groups
    for match in middleware_route_regex.finditer(content):
      method = match.group(1)
      uri = match.group(2)
      action = match.group(3).strip()
      middleware_str = match.group(4)
      middleware = [m.strip(" '") for m in re.findall(
          r"'([^']*)'", middleware_str)] if middleware_str else []
      routes.append({
          'method': method,
          'uri': uri,
          'action': action,
          'middleware': middleware,
          'name': None
      })

    # Named middleware routes outside groups
    for match in named_middleware_route_regex.finditer(content):
      method = match.group(1)
      uri = match.group(2)
      action = match.group(3).strip()
      name = match.group(4)
      middleware_str = match.group(5)
      middleware = [m.strip(" '") for m in re.findall(
          r"'([^']*)'", middleware_str)] if middleware_str else []
      routes.append({
          'method': method,
          'uri': uri,
          'action': action,
          'middleware': middleware,
          'name': name
      })

  except (IOError, OSError, UnicodeDecodeError) as e:
    print(f"Error reading or parsing file {file_path}: {e}")
    return []

  return routes


def find_route_files(directory, exclude_dirs=None):
  """
  Recursively finds PHP files that likely contain route definitions.

  Args:
      directory (str): The directory to search.

  Yields:
      str: The path to a potential route file.
  """
  if exclude_dirs is None:
    exclude_dirs = {'vendor', 'node_modules',
                    'storage', 'bootstrap', '.git', '.idea'}
  else:
    exclude_dirs = set(exclude_dirs)

  # 注意：这里把原本的 `_` 换成了 `dirs`，因为我们需要操作它
  for root, dirs, files in os.walk(directory):

    # 【关键步骤】：原地修改 dirs 列表，过滤掉需要排除的目录
    # 使用 dirs[:] = ... 可以修改原列表对象，而不是创建一个新变量
    # 这样 os.walk 就不会进入被排除的文件夹中
    dirs[:] = [d for d in dirs if d not in exclude_dirs]

    # 接下来就是正常的匹配文件逻辑
    for file in files:
      # if file.endswith('.php') and ('routes' in file.lower() or 'route' in file.lower()):
      if file.endswith('.php') and ('routes' in file.lower()):
        yield os.path.join(root, file)


def main():
  """
  Main function to scan for route files and extract route information.
  """
  # Replace with the root directory of your Laravel project
  # Or e.g., '/path/to/your/laravel/project'
  project_root = '/mnt/d/vulnerability_discovery/漏洞挖掘/目标漏洞挖掘/BT/New/ingredi/app/'
  route_files_found = False

  for file_path in find_route_files(project_root):
    route_files_found = True
    print(f"Processing file: {file_path}")
    routes = extract_routes(file_path)
    if routes:
      for route in routes:
        print(f"  - Method: {route.get('method', 'N/A')}, URI: {route.get('uri', 'N/A')}, Action: {route.get('action', 'N/A')}, Middleware: {route.get('middleware', []), 'N/A'}, Name: {route.get('name', 'N/A')}")
    else:
      print("  - No routes found.")

  if not route_files_found:
    print("No route files found in the specified directory (or subdirectories).  Check your project_root.")


if __name__ == "__main__":
  main()
