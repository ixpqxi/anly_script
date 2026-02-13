import json

result = {}


with open("result/vuln_info_1day.json", "r", encoding="utf-8") as f:
  data = json.load(f)

for d in data:
  platform = d["devops platform"]
  version = d["version"]
  cve_id = d["cve_id"]
  if platform not in result:
    result[platform] = {}
  if version not in result[platform]:
    result[platform][version] = set()
  result[platform][version].add(cve_id)

for platformin in result:
  print("="*10 + platformin + "="*10)
  for versionin in result[platformin]:
    print("\t\t" + versionin)
    print(json.dumps(list(result[platformin][versionin]), indent=2))
