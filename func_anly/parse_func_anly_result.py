import csv
import json
import os
from typing import Dict, List, Set

from dotenv import load_dotenv
from json_repair import repair_json
from pydantic import BaseModel, Field, computed_field

load_dotenv()

project_name_list = ['pretix_pretix', 'web-infra-dev_rspack', 'NaiboWang_EasySpider', 'GoogleChrome_lighthouse', 'ktorio_ktor', 'nottelabs_notte', 'cogentcore_core', 'tenox7_wrp', 'QwikDev_qwik', 'HelloZeroNet_ZeroNet', 'syt123450_giojs', 'expo_expo', 'jkbrzt_cloudtunes', 'dpgaspar_Flask-AppBuilder', 'cakephp_cakephp', 'elliotgao2_toapi', 'microsoft_playwright', 'wooey_Wooey', 'taiga-family_taiga-ui', 'rejetto_hfs', 'openRin_Rin', 'phcode-dev_phoenix', 'mufeedvh_binserve', 'zalando_tailor', 'nickola_web-console', 'zhayujie_bot-on-anything', 'angular_angular', 'sparklemotion_mechanize', 'mayswind_AriaNg-Native', 'sensepost_gowitness', 'MCP-UI-Org_mcp-ui', 'varabyte_kobweb', 'kurogai_100-redteam-projects', 'Rudolf-Barbu_Ward', 'JetBrains_kotlinconf-app', 'tomaka_rouille', 'abhijithvijayan_web-extension-starter', 'whwlsfb_JDumpSpider', 'aurelia_aurelia', 'labstack_echo', 'ionic-team_ionic-framework', 'elysiajs_elysia', 'nerfstudio-project_viser', 'danielgtaylor_huma', 'Tencent_westore', 'schollz_hostyoself', 'slimkit_plus', 'geoserver_geoserver', 'digicorp_propeller', 'yacy_yacy_search_server', 'django_django', 'nitin42_react-perf-devtool', 'arthaud_git-dumper', 'poem-web_poem', 'vugu_vugu', 'zhuifengshaonianhanlu_pikachu', 'gofiber_fiber', 'ffuf_ffuf', 'StractOrg_stract', 'AUTOMATIC1111_stable-diffusion-webui', 'delight-im_Android-AdvancedWebView', 'nicolargo_glances', 'express-rate-limit_express-rate-limit', 'amplication_amplication', 'ivanceras_sauron', 'ctf-wiki_ctf-wiki', 'alextselegidis_easyappointments', 'sanic-org_sanic', 'GenieFramework_Genie.jl', 'apache_dubbo', 'devhubapp_devhub', 'JetBrains_kotless', 'biomejs_biome', 'flexxui_flexx', 'OJ_gobuster', 'reflex-dev_reflex', 'koute_cargo-web', 'nextapps-de_flexsearch', 'rialto-php_puphpeteer', 'chinedufn_percy', 'lowlighter_matcha',
                     'fastapi_fastapi', 'SEAbdulbasit_MusicApp-KMP', 'WebReflection_linkedom', 'eythaann_Seelen-UI', 'yudai_gotty', 'chai2010_advanced-go-programming-book', 'gobuffalo_buffalo', 'koute_stdweb', 'HaoZhang95_Python24', 'tiagozip_cap', 'anzhihe_Free-Web-Books', 'httpie_cli', 'binux_yaaw', 'avwo_whistle', 'leptos-rs_leptos', 'aurelia_framework', 'formatjs_formatjs', 'searchkit_searchkit', 'MechanicalSoup_MechanicalSoup', 'eidheim_Simple-Web-Server', 'yahoo_fluxible', 'Kinto_kinto', 'sparckles_Robyn', 'appwrite_appwrite', 'adnanh_webhook', 'devfeel_dotweb', 'vert-x3_vertx-web', 'salvo-rs_salvo', 'justin-schroeder_arrow-js', 'JoyChou93_java-sec-code', 'flexn-io_renative', 'material-components_material-components-web', 'undertow-io_undertow', 'ferronweb_ferron', 'evroon_bracket', 'actix_actix-web', 'photonixapp_photonix', 'yeyupiaoling_Whisper-Finetune', 'htty_htty', 'WebAV-Tech_WebAV', 'finagle_finch', 'szabodanika_microbin', 'tinyfish-io_agentql', 'twilco_kosmonaut', 'DioxusLabs_dioxus', 'turms-im_turms', 'ranile_gloo', 'BrainJS_brain.js', 'google_tamperchrome', 'tariqbuilds_linux-dash', 'go-gorm_gorm', 'rjsf-team_react-jsonschema-form', 'numberwolf_h265web.js', 'tobegit3hub_seagull', 'pod4g_hiper', 'KidkArolis_jetpack', 'sitespeedio_sitespeed.io', 'divkit_divkit', 'FrigadeHQ_remote-storage', 'handtracking-io_yoha', 'greyli_helloflask', 'SudhanPlayz_Discord-MusicBot', 'smapiot_piral', 'LukeMathWalker_pavex', 'falconry_falcon', 'rack_rack', 'totaljs_framework', 'GoogleChrome_web.dev', 'oblador_loki', 'MasoniteFramework_masonite', 'stackshareio_awesome-stacks', 'sl1673495_blogs', 'ppy_osu-web', 'epi052_feroxbuster', 'web-infra-dev_modern.js', 'go-dev-frame_sponge', 'donnemartin_system-design-primer', 'parcel-bundler_parcel', 'ammarahm-ed_react-native-actions-sheet', 'xkcoding_spring-boot-demo']


class Operation(BaseModel):
  operation_type: str
  resource_objects: List[str]


class ResourceAnalysis(BaseModel):
  reason: str
  is_resource_operation: bool
  entry_type: str
  entry_detail: str
  confidence: str
  operations: List[Operation]

#### result ####


class OperationDetail(BaseModel):
  operation_type: Set = Field(default_factory=set)
  entry_type: Set = Field(default_factory=set)


class ResourceDetail(BaseModel):
  # 资源种类数量
  category: int = 0
  # 具体的资源名称及其操作集合: {"User": {"Read", "Update"}}
  resource_name: Dict[str, OperationDetail] = Field(default_factory=dict)


class StatisticsResult(BaseModel):
  # 总接口数/调用数
  endpoint: int = 0
  # 涉及资源操作的接口数
  resource_operation_endpoint: int = 0
  # 多资源操作的接口数
  multiple_resource_operation_endpoint: int = 0
  # 资源详情
  resource: ResourceDetail = Field(default_factory=ResourceDetail)
  # 资源操作总次数
  resource_operation_num: int = 0

  # 平均值：resource_operation_num / resource_operation_endpoint
  @computed_field
  @property
  def avg_each_endpoint_resource_operation_num(self) -> float:
    if self.resource_operation_endpoint > 0:
      return round(self.resource_operation_num / self.resource_operation_endpoint, 2)
    else:
      return 0.0

  # 平均值：resource_operation_num / resource.category
  @computed_field
  @property
  def avg_each_resource_operation_endpoint(self) -> float:
    if self.resource.category > 0:
      return round(self.resource_operation_num / self.resource.category, 2)
    else:
      return 0.0

  @computed_field
  @property
  def multiple_entry_resource_num(self) -> int:
    result = 0
    for r_anme, op_detail in self.resource.resource_name.items():
      if len(op_detail.entry_type) > 1:
        result += 1
    return result

  @computed_field
  @property
  def multiple_entry_resource_rate(self) -> float:
    if self.resource.category > 0:
      return round(self.multiple_entry_resource_num / self.resource.category, 2)
    else:
      return 0.0


index_table = {}
result: Dict[str, StatisticsResult] = {}


def parse_single_result(obj: str):
  global result
  global index_table

  custom_id = obj["custom_id"]
  message = obj["response"]["body"]["choices"][0]["message"]

  project_name = index_table[int(custom_id)]

  # 如果不在统计列表内则跳过
  if project_name not in project_name_list:
    return

  if project_name not in result:
    result[project_name] = StatisticsResult()
  try:
    content = ResourceAnalysis.model_validate_json(
        repair_json(message["content"]))
  except Exception as e:
    return

  result[project_name].endpoint += 1
  if content.is_resource_operation:
    # if project_name == "yewstack_yew":
    #   print(content.model_dump_json())
    result[project_name].resource_operation_endpoint += 1
    if len(content.operations) > 1:
      result[project_name].multiple_resource_operation_endpoint += 1

    for operation in content.operations:
      result[project_name].resource_operation_num += len(
          operation.resource_objects)
      for resource in operation.resource_objects:
        if resource not in result[project_name].resource.resource_name:
          result[project_name].resource.resource_name[resource] = OperationDetail()
          result[project_name].resource.category += 1
        result[project_name].resource.resource_name[resource].operation_type.add(
            operation.operation_type)
        result[project_name].resource.resource_name[resource].entry_type.add(
            content.entry_type)


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


def print_table():
  res = ""

  '''
  打印结果数据表格

  表格格式为：

  | ID | 项目名称 | 总函数数量 | 资源种类数量 | 涉及资源操作的端点数 | 资源操作总数 | 资源操作总数/资源操作接口数 |
  | --- | --- | --- | --- | --- | --- | --- |
  | index | project_name | endpoint | resource.category | resource_operation_endpoint | resource_operation_num | avg_each_endpoint_resource_operation_num |
  '''
  res += "| ID | 项目名称 | 总函数数量 | 资源种类数量 | 涉及资源操作的端点数 | 资源操作总数 | 资源操作总数/资源操作接口数 |\n"
  res += "| --- | --- | --- | --- | --- | --- | --- |\n"
  for index, (project_name, r) in enumerate(result.items()):
    res += f"| {index} | {project_name} | {r.endpoint} | {r.resource.category} | {r.resource_operation_endpoint} | {r.resource_operation_num} | {r.avg_each_endpoint_resource_operation_num} |\n"
  return res


def print_target_table(target_project: str):
  for index, (project_name, r) in enumerate(result.items()):
    if project_name == target_project:
      print(f"| {index} | {project_name} | {r.endpoint} | {r.resource.category} | {r.resource_operation_endpoint} | {r.resource_operation_num} | {r.avg_each_endpoint_resource_operation_num} | {r.avg_each_resource_operation_endpoint} |")
      print(r.resource.resource_name)


def print_resource_name():
  for project_name, r in result.items():
    with open(f"result/resource_name_web/{project_name}.json", "w", encoding="utf-8") as f:
      f.write(json.dumps(list(r.resource.resource_name.keys())))

    with open(f"result/optype_web/{project_name}.json", "w", encoding="utf-8") as f:
      f.write(r.resource.model_dump_json())


def save_to_csv(file_path):
  with open(file_path, "w", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "项目名称", "总函数数量", "资源种类数量", "涉及资源操作的端点数", "多操作端点数量",
                    "资源操作总数", "资源操作总数/资源操作接口数", "资源操作总数/资源种类数量", "多入口资源数量", "多入口资源比例"])
    for index, (project_name, r) in enumerate(result.items()):
      writer.writerow([index+121, project_name, r.endpoint, r.resource.category, r.resource_operation_endpoint, r.multiple_resource_operation_endpoint, r.resource_operation_num,
                      r.avg_each_endpoint_resource_operation_num, r.avg_each_resource_operation_endpoint, r.multiple_entry_resource_num, r.multiple_entry_resource_rate])


if __name__ == "__main__":
  betch_result_file = os.getenv("BATCH_RESULT_FILE")
  index_table_file = os.getenv("OUTPUT_INDEX_TABLE_FILE")

  load_index_table(index_table_file)

  parse_result_file(betch_result_file)
  # print_resource_name()
  # print(print_target_table("yewstack_yew"))
  save_to_csv("result/func_anly_result_web_v5-1.csv")
  # with open("result/func_anly_result.md", "w", encoding="utf-8") as f:
  #   f.write(print_table())
  #   f.write(print_table())
  #   f.write(print_table())
