from typing import Dict, List

from json_repair import repair_json
from pydantic import BaseModel, Field, computed_field

# {'is_web': True, 'target_category': 'Web API', 'vulnerability_type': 'Denial of Service', 'is_stateful': False, 'dependency_analysis': {'requires_control_flow': False, 'requires_data_flow': False, 'reasoning': 'The vulnerability can be exploited with a single, stateless HTTP request containing a malformed JSON payload. No prior application state or server-generated data is required.', 'details': {'control_flow_chain': [], 'data_flow_pairs': []}}}


class DataFlowPair(BaseModel):
  """描述数据流中生产者与消费者的对应关系"""
  producer_step: str = Field(..., description="数据的来源步骤，例如 GET /api/profile")
  extracted_data: str = Field(..., description="提取的数据名称，例如 user_id")
  consumer_step: str = Field(..., description="使用该数据的步骤，例如 POST /api/delete")


class DependencyDetails(BaseModel):
  """依赖关系的具体细节"""
  control_flow_chain: List[str] = Field(
      default_factory=list,
      description="控制流步骤链"
  )
  data_flow_pairs: List[DataFlowPair] = Field(
      default_factory=list,
      description="数据流对列表"
  )


class DependencyAnalysis(BaseModel):
  """漏洞依赖性分析模型"""
  requires_control_flow: bool
  requires_data_flow: bool
  reasoning: str = Field(..., description="发现依赖关系的简要解释")
  details: DependencyDetails


class VulnerabilityReport(BaseModel):
  """主模型：漏洞扫描/分析对象"""
  is_web: bool = Field(..., description="目标是否为 Web 应用或 Web API")
  target_category: str = Field(..., description="目标类别，如 Web App, API 等")
  vulnerability_type: str = Field(..., description="漏洞类型，如 IDOR, SQLi, RCE")
  is_stateful: bool = Field(..., description="如果控制流或数据流为 True, 则该项为 True")
  dependency_analysis: DependencyAnalysis
  # report_path: str


class VulnTypeInfo(BaseModel):
  stateful_count: int = 0
  unstateful_count: int = 0


class StatisticsResult(BaseModel):
  count: int = 0
  is_web_count: int = 0
  is_stateful_count: int = 0
  req_control_and_data_flow_count: int = 0

  @computed_field
  @property
  def req_control_count(self) -> int:
    return len(self.req_control_folw_vulns)

  @computed_field
  @property
  def req_data_count(self) -> int:
    return len(self.req_data_flow_vulns)

  req_control_folw_vulns: List[VulnerabilityReport] = Field(
      default_factory=list)
  req_data_flow_vulns: List[VulnerabilityReport] = Field(default_factory=list)
  vuln_type_statistics: Dict[str, VulnTypeInfo] = Field(default_factory=dict)


def statistics_result():
  statistics_result = StatisticsResult()
  error_count = 0

  with open("./result/state_dep_vuln/judgment_result.jsonl", "r", encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      line = repair_json(line)

      # result = json.loads(line)
      try:
        report: VulnerabilityReport = VulnerabilityReport.model_validate_json(
            line)
      except Exception as e:
        error_count += 1
        print("Error!", e)
        continue

      statistics_result.count += 1
      if report.is_web:
        statistics_result.is_web_count += 1
      else:
        continue

      # 漏洞类型统计
      if report.vulnerability_type not in statistics_result.vuln_type_statistics:
        statistics_result.vuln_type_statistics[report.vulnerability_type] = VulnTypeInfo(
        )

      if report.is_stateful:
        statistics_result.is_stateful_count += 1
        statistics_result.vuln_type_statistics[report.vulnerability_type].stateful_count += 1
      else:
        statistics_result.vuln_type_statistics[report.vulnerability_type].unstateful_count += 1

      is_control_flow = report.dependency_analysis.requires_control_flow
      is_data_flow = report.dependency_analysis.requires_data_flow

      if is_control_flow and is_data_flow:
        statistics_result.req_control_and_data_flow_count += 1
      if is_control_flow:
        statistics_result.req_control_folw_vulns.append(report)
      if is_data_flow:
        statistics_result.req_data_flow_vulns.append(report)

  with open("./result/state_dep_vuln/statistics_result_new_c.json", "w", encoding="utf-8") as f:
    f.write(statistics_result.model_dump_json(indent=2))
  print("error count:", error_count)


def anly_control_and_data_flow():
  with open("./result/state_dep_vuln/statistics_result.json", "r", encoding="utf-8") as f:
    statistics_result = StatisticsResult.model_validate_json(f.read())

  vuln_types = {}

  for report in statistics_result.req_control_folw_vulns:
    if report.dependency_analysis.requires_control_flow and report.dependency_analysis.requires_data_flow:
      vuln_types[report.vulnerability_type] = vuln_types.get(
          report.vulnerability_type, 0) + 1

  for report in statistics_result.req_data_flow_vulns:
    if report.dependency_analysis.requires_control_flow and report.dependency_analysis.requires_data_flow:
      vuln_types[report.vulnerability_type] = vuln_types.get(
          report.vulnerability_type, 0) + 1

  print(vuln_types)


# def statstics_result():


def anly_statistics_result():
  with open("./result/state_dep_vuln/statistics_result_new.json", "r", encoding="utf-8") as f:
    statistics_result = StatisticsResult.model_validate_json(f.read())

  is_web_count = statistics_result.is_web_count
  is_stateful_count = statistics_result.is_stateful_count
  req_control_and_data_flow_count = statistics_result.req_control_and_data_flow_count
  req_control_count = statistics_result.req_control_count
  req_data_count = statistics_result.req_data_count

  print("stateful:", is_stateful_count / is_web_count)
  print("unstateful:", (is_web_count - is_stateful_count) / is_web_count)
  print("req_control_and_data_flow:",
        req_control_and_data_flow_count / is_web_count)
  print("req_control:", req_control_count / is_web_count)
  print("req_data:", req_data_count / is_web_count)


if __name__ == "__main__":
  statistics_result()
  # anly_statistics_result()
  # anly_control_and_data_flow()
