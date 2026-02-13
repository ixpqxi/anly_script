Analyze the following function code to determine its resource operation status and its specific entry point characteristics.

### Function to Analyze

```
{function_definition}
```

### Evaluation Criteria

**1. Resource Operation Classification:**
* **IS a resource operation:** Queries, creates, updates, or deletes data (CRUD); manipulates domain objects (User, Project, etc.); accesses DBs, files, caches, or APIs; changes system state.
* **NOT a resource operation:** Pure utility/helper functions (formatting, conversion); authorization checks ONLY; simple UI rendering; static config.

**2. Route Entry Type Classification:**
Identify how this function is triggered or exposed. Categories include but are not limited to:
* `Web`: Standard MVC controller, HTML-returning routes.
* `REST`: JSON/XML based RESTful API endpoints.
* `GraphQL`: GraphQL resolvers or schema definitions.
* `RPC`: gRPC, Thrift, Dubbo or other Remote Procedure Calls.
* `Worker`: Message queue consumers (RabbitMQ, Kafka), cron jobs, or background tasks.
* `Serverless`: Cloud functions (AWS Lambda, Azure Functions, etc.).
* `Socket`: WebSocket or raw TCP/UDP socket handlers.
* `CLI`: Command-line interface commands or scripts.
* `Internal`: Private methods or helper functions not directly exposed.
* `Other`: Any other trigger type not listed above (please specify in `entry_type`).

### Instructions

1.  **Operation Analysis:** Determine if the function is a resource operation.
2.  **Entry Point Discovery:** Analyze decorators (e.g., `@app.route`, `@Subscribe`), method signatures, and parameter types to identify the entry point. **If the type is not among the standard list, provide a custom label.**
3.  **Data Extraction:** If `is_resource_operation` is `true`, map out the CRUD types and the specific domain objects involved.
4.  **Output:** Return the result **STRICTLY** as a JSON object.

### Output Format

```json
{{
  "reason": "A brief explanation of the resource classification and entry type logic",
  "is_resource_operation": boolean,
  "entry_type": "The identified type (e.g., REST, GraphQL, Worker, or a custom type like 'CloudEvent')",
  "entry_detail": "Specific routing info (e.g., 'POST /users', 'Topic: user.signup', 'Timer: 0 0 * * *')",
  "confidence": "high|medium|low",
  "operations": [
    {{
      "operation_type": "Create|Read|Update|Delete|Other",
      "resource_objects": ["ObjectName1"]
    }}
  ]
}}

### Example Output (for a custom type)

{{
  "reason": "Function listens to a Kafka topic and updates the Inventory stock level.",
  "is_resource_operation": true,
  "entry_type": "Web",
  "entry_detail": "Topic: inventory.updates.v1",
  "confidence": "high",
  "operations": [
    {{
      "operation_type": "Update",
      "resource_objects": ["Inventory"]
    }}
  ]
}}