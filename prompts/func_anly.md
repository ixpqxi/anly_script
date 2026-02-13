Analyze the following function code to determine if it performs resource operations and identify the details of those operations.

### Function to Analyze
```
{function_definition}
```

### Evaluation Criteria

**1. A resource operation function:**

* Queries, creates, updates, or deletes data (CRUD operations).
* Manipulates domain objects (e.g., User, Project, Issue, Attachment).
* Accesses databases, files, caches, or external APIs.
* Performs business logic that changes the system state.

**2. NOT a resource operation function:**

* Pure utility/helper functions (formatting, unit conversion, string manipulation).
* Authorization/permission check logic ONLY (without data fetching).
* Simple view rendering or UI-only logic.
* Static configuration or constant setup functions.

### Instructions

1. First, determine if the function is a resource operation based on the criteria above.
2. If `is_resource_operation` is `false`, set `operations` to an empty list `[]`.
3. If `is_resource_operation` is `true`, perform a deep dive to identify all specific operations, their types, the objects involved, and their line ranges.

### Output Format

Return the result STRICTLY as a JSON object with the following structure:
{{
  "reason": "A brief one-sentence explanation of the classification",
  "is_resource_operation": boolean,
  "confidence": "high" | "medium" | "low",
  "operations": [
    {{
      "operation_type": "Create|Read|Update|Delete|Other",
      "resource_objects": ["ObjectName1", "ObjectName2"]
    }}
  ]
}}

### Example Output

{{
  "reason": "Function fetches User records and updates their last_login timestamp.",
  "is_resource_operation": true,
  "confidence": "high",
  "operations": [
    {{
      "operation_type": "Read",
      "resource_objects": ["User"]
    }},
    {{
      "operation_type": "Update",
      "resource_objects": ["User"]
    }}
  ]
}}