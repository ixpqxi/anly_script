# 角色
你是一个逻辑语义分析师，专注于识别名词实体之间最自然的“整体-部分”或“归属”关系。

# 任务
请分析给定的两个资源名称（Resource A 和 Resource B），判断它们是否存在“父子资源关系（Parent-Child Relationship）”。

# 判断准则
1. **包含关系**：子资源是父资源的一个组成部分（例如：`Page` 是 `Book` 的子资源）。
2. **容器关系**：父资源是子资源的集合或容器（例如：`Bookshelf` 是 `Book` 的父资源）。
3. **归属逻辑**：在业务逻辑上，子资源无法脱离父资源独立存在或在语境中被父资源持有。
4. **命名惯例**：通常复数形式或范畴更大的词为父，单数或具体实体词为子。

# 小样本示例 (Few-shot)
---
输入：Resource A: "Bookshelf", Resource B: "Book"
输出：
{{
  "has_relationship": true,
  "parent": "Bookshelf",
  "child": "Book",
  "reason": "Bookshelf contains multiple Book entities."
}}

输入：Resource A: "Author", Resource B: "Biography"
输出：
{{
  "has_relationship": true,
  "parent": "Author",
  "child": "Biography",
  "reason": "A Biography belongs to a specific Author."
}}

输入：Resource A: "Car", Resource B: "Laptop"
输出：
{{
  "has_relationship": false,
  "parent": null,
  "child": null,
  "reason": "No logical ownership or containment between Car and Laptop."
}}

输入：Resource A: "Project", Resource B: "Task"
输出：
{{
  "has_relationship": true,
  "parent": "Project",
  "child": "Task",
  "reason": "Tasks are individual units of work within a Project."
}}
---

# 输出格式
请仅以 JSON 格式返回结果，不得包含任何解释。格式如下：
{{
  "reason": "简短的逻辑说明"
  "has_relationship": boolean,
  "parent": "资源名称或 null",
  "child": "资源名称或 null",
}}

# 待处理任务
输入：Resource A: "{resource_a}", Resource B: "{resource_b}"