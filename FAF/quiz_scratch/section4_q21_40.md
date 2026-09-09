### Question 21
**Difficulty:** Advanced

A developer creates the following pyfunc model:

```python
class CustomChain(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        import openai
        self.client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.system_prompt = context.artifacts["system_prompt"]

    def predict(self, context, model_input):
        query = model_input["query"].iloc[0]
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": self.system_prompt},
                      {"role": "user", "content": query}]
        )
        return response.choices[0].message.content
```

They log it with `mlflow.pyfunc.log_model(artifact_path="chain", python_model=CustomChain(), artifacts={"system_prompt": "./system_prompt.txt"})`. What does `context.artifacts["system_prompt"]` return during serving?

A) The string `"./system_prompt.txt"` — the artifacts dictionary stores the local file path as specified at log time, and the serving environment uses this path to locate the file on the serving container's local filesystem.
B) The resolved local file path to the `system_prompt.txt` file as it exists in the serving container (e.g., `/tmp/mlflow-artifacts/system_prompt.txt`) — MLflow copies the artifact to the serving container and provides its local path via the context.
C) The contents of `system_prompt.txt` as a Python string — MLflow reads the file and passes its text content directly through `context.artifacts`.
D) A Spark DataFrame containing the system prompt text — MLflow standardizes all artifact returns to Spark DataFrames for compatibility with Databricks' distributed serving infrastructure.

**Correct Answer:** B
**Explanation:** B is correct. When artifacts are logged with `mlflow.pyfunc.log_model()`, MLflow copies those files into the MLflow artifact store (e.g., DBFS or a cloud storage path). When the model is deployed to a Model Serving endpoint, MLflow downloads these artifacts to the serving container's local filesystem. `context.artifacts["system_prompt"]` returns the LOCAL FILE PATH on the serving container where `system_prompt.txt` was copied — NOT the original relative path, NOT the file contents, and NOT a DataFrame. The code then uses this path as `self.system_prompt = context.artifacts["system_prompt"]` — but note this actually stores the file path, so to get the file contents the developer would need `open(context.artifacts["system_prompt"]).read()`. A is wrong because the original relative path `"./system_prompt.txt"` is the LOG-time path — it does not exist in the serving container; MLflow copies and relocates the file. C is wrong because `context.artifacts` provides paths, not file contents — the developer must explicitly read the file using the path. D is wrong because MLflow artifacts are files, not DataFrames; Databricks Model Serving does not convert file artifacts to DataFrames.
**Source:** Section 4: Assembling and Deploying – Objective 1: Code a chain using a pyfunc model — docs.databricks.com (search: "mlflow.pyfunc PythonModel custom")

---

### Question 22
**Difficulty:** Advanced

A team uses OAuth M2M (Machine-to-Machine) authentication for their production application to call a Databricks Model Serving endpoint. Why is OAuth M2M preferred over using a personal access token (PAT) for this production scenario?

A) OAuth M2M tokens are valid for 30 days without renewal, while PATs expire after 24 hours by default — the longer validity period reduces operational overhead of credential rotation in production systems.
B) OAuth M2M uses a Service Principal identity, which has workspace-level permissions that PATs lack — Service Principals can access more Unity Catalog resources than user-level PATs are permitted to access.
C) OAuth M2M generates short-lived tokens automatically via a client credentials flow, eliminating the need to store long-lived credentials — a Service Principal's `client_id` and `client_secret` grant access without persisting a long-lived token, reducing the blast radius of credential compromise.
D) OAuth M2M is the only authentication method supported by Databricks Model Serving endpoints — PATs are only valid for the Databricks REST API for notebook and cluster management, not for Model Serving inference calls.

**Correct Answer:** C
**Explanation:** C is correct. OAuth M2M (Machine-to-Machine) authentication is preferred for production because it uses a Service Principal with short-lived, auto-refreshed tokens generated via the OAuth 2.0 Client Credentials flow. The application stores only the Service Principal's `client_id` and `client_secret` (not a long-lived token), and the OAuth library automatically exchanges these for short-lived access tokens (typically valid for 1 hour) and refreshes them. If a token is compromised, it expires quickly — limiting the blast radius. PATs are long-lived tokens (configurable, often 90+ days) that are more dangerous if leaked. A is wrong because PAT expiry is configurable (not fixed at 24 hours), and OAuth M2M tokens are SHORT-lived (1 hour), not 30 days — the advantage is that short-lived tokens are MORE secure, not less convenient. B is wrong because PATs and Service Principals can be granted identical Unity Catalog permissions — the distinction is identity type and token management, not permission scope. D is wrong because PATs are also supported for Model Serving endpoint inference calls — OAuth M2M is preferred, not mandatory.
**Source:** Section 4: Assembling and Deploying – Objective 2: Control access to resources from model serving endpoints — docs.databricks.com (search: "Model serving endpoint permissions Databricks")

---

### Question 23
**Difficulty:** Advanced

A developer logs a LangChain chain with:
```python
mlflow.langchain.log_model(
    lc_model=chain,
    artifact_path="rag_chain",
    input_example={"context": "Sample context text.", "question": "What is the policy?"}
)
```

Later, a colleague loads the model with `mlflow.pyfunc.load_model(model_uri)` and calls `model.predict(input_data)`. What format must `input_data` be in, and why?

A) `input_data` must be a Python dictionary `{"context": "...", "question": "..."}` — `mlflow.pyfunc.load_model` always accepts raw dictionaries as inputs for LangChain models.
B) `input_data` must be a Pandas DataFrame with columns matching the input schema (i.e., `pd.DataFrame([{"context": "...", "question": "..."}])`) — MLflow's pyfunc interface standardizes all model inputs as DataFrames, and the logged `input_example` defines the expected column names.
C) `input_data` must be a JSON string `'{"context": "...", "question": "..."}'` that `mlflow.pyfunc.load_model` automatically parses before passing to the chain's invoke method.
D) `input_data` can be any Python object — `mlflow.pyfunc.load_model` for LangChain models bypasses MLflow's type-checking system and passes whatever object is provided directly to the chain's `invoke()` method without any schema validation.

**Correct Answer:** B
**Explanation:** B is correct. `mlflow.pyfunc.load_model()` returns an MLflow pyfunc model that implements the standard pyfunc interface. For this interface, `predict()` expects a Pandas DataFrame whose column names match the model signature's input schema. The `input_example` provided at log time (`{"context": "...", "question": "..."}`) is used to infer the model signature, which defines two string columns: `context` and `question`. The caller must provide a DataFrame with those exact column names: `pd.DataFrame([{"context": "actual context", "question": "actual question"}])`. A is wrong because the pyfunc interface does NOT accept raw Python dictionaries — it requires a Pandas DataFrame; passing a raw dict raises a signature validation error. C is wrong because raw JSON strings are not the expected input format for `pyfunc.predict()` — while JSON is the wire format for REST API calls to the serving endpoint, the local Python interface requires a DataFrame. D is wrong because pyfunc enforces the model signature when a signature is present (which it is, since `input_example` was provided) — it validates that the input DataFrame has the correct columns and types.
**Source:** Section 4: Assembling and Deploying – Objective 3 & 4: Code a simple chain and RAG elements — docs.databricks.com (search: "Log and load LangChain models MLflow Databricks")

---

### Question 24
**Difficulty:** Advanced

A Delta Sync Vector Search index uses `pipeline_type="CONTINUOUS"`. The source Delta table receives 10,000 new document chunks per hour via a streaming Spark job. A developer asks: "At what cost does CONTINUOUS sync come compared to TRIGGERED, and when does TRIGGERED become the right choice?"

A) CONTINUOUS sync has zero additional cost compared to TRIGGERED sync — the Vector Search endpoint incurs the same fixed hourly compute charge regardless of whether CONTINUOUS or TRIGGERED mode is selected.
B) CONTINUOUS sync incurs higher ongoing compute costs because the sync pipeline runs persistently, consuming Vector Search endpoint resources continuously to monitor and process Delta table changes. TRIGGERED sync is more cost-efficient when data freshness requirements allow periodic (e.g., daily or weekly) updates rather than near-real-time indexing.
C) CONTINUOUS sync is cheaper than TRIGGERED sync because it processes changes incrementally (small batches), while TRIGGERED sync must reprocess the entire index from scratch on each sync, consuming more total compute per update cycle.
D) TRIGGERED sync always costs exactly the same per-sync as CONTINUOUS mode costs per-hour — the cost difference depends only on how frequently the team triggers manual syncs, not on the pipeline type itself.

**Correct Answer:** B
**Explanation:** B is correct. CONTINUOUS sync maintains an always-running sync pipeline that monitors the source Delta table's Change Data Feed in near real time and processes new changes as they arrive. This pipeline consumes Vector Search endpoint compute resources continuously — even during low-activity periods. TRIGGERED sync only consumes resources when explicitly invoked — the sync process runs to completion and then stops, consuming no resources until the next trigger. For workloads where data freshness requirements allow periodic updates (e.g., a knowledge base updated daily, a product catalog refreshed weekly), TRIGGERED sync is significantly more cost-efficient. CONTINUOUS mode is justified when freshness is critical (e.g., indexing news articles for a real-time news chatbot). A is wrong because CONTINUOUS and TRIGGERED sync do NOT have the same cost — CONTINUOUS incurs ongoing compute costs from the persistent pipeline. C is wrong because TRIGGERED sync is typically incremental too (using CDF to process only changed rows), not a full reindex; and TRIGGERED is cheaper for infrequent updates, not more expensive. D is wrong because the cost difference is inherent to the pipeline type (always-running vs. on-demand), not solely determined by trigger frequency.
**Source:** Section 4: Assembling and Deploying – Objective 10: Configure vector search based on requirements — docs.databricks.com (search: "Mosaic AI Vector Search configuration")

---

### Question 25
**Difficulty:** Advanced

A team's CI/CD pipeline uses Databricks Asset Bundles. The `databricks.yml` defines three environments: `dev`, `staging`, and `production`. The developer runs `databricks bundle deploy --target staging`. What happens, and what safety does this provide?

A) `databricks bundle deploy --target staging` deploys ALL resources defined in `databricks.yml` to the `staging` workspace or the staging-specific resource prefix, using staging-specific variable values (e.g., endpoint names, catalog names) defined in the target configuration — it does NOT touch the `dev` or `production` environments.
B) `databricks bundle deploy --target staging` validates the `databricks.yml` syntax only but does not deploy any resources — the `--target` flag is for specifying which environment's configuration to validate, and deployment requires an additional `--execute` flag.
C) `databricks bundle deploy --target staging` deploys to staging AND automatically promotes validated resources to production if the staging deployment succeeds within a 5-minute health check window — this implements automatic blue-green promotion.
D) `databricks bundle deploy --target staging` replaces the `dev` resources with staging resources — in Databricks Asset Bundles, each new deployment replaces the previous environment tier, migrating resources upward through the promotion pipeline.

**Correct Answer:** A
**Explanation:** A is correct. Databricks Asset Bundles support multi-environment deployment through target configurations in `databricks.yml`. Each target can specify different variable values (e.g., `catalog: staging_catalog`, `model_name: rag_app_staging`) and different workspace URLs. When `databricks bundle deploy --target staging` is run: (1) DABs uses the `staging` target's variable values to parameterize the resource definitions. (2) It deploys only to the staging environment — dev and production are completely untouched. (3) This provides the safety guarantee that staging deployments are isolated — you can test staging without risk of breaking production. The promotion pipeline typically requires an explicit second `databricks bundle deploy --target production` command after staging validation. B is wrong because `databricks bundle validate` (without `deploy`) is the syntax-only validation command — `bundle deploy` always executes the deployment. C is wrong because DABs never automatically promotes between environments — each environment requires its own explicit `deploy` command; automatic promotion would be dangerous for production systems. D is wrong because environments in DABs are independent — deploying to staging does not modify dev resources; each target deploys to its own isolated configuration.
**Source:** Section 4: Assembling and Deploying – Objective 12: Apply CI/CD best practices — docs.databricks.com (search: "Databricks Asset Bundles CI/CD")

---

### Question 26
**Difficulty:** Advanced

A company has a knowledge base of 8 million document chunks. They need to choose Vector Search index configuration. Requirements: search latency must be under 50ms at P95, the knowledge base is updated once per week, and embedding costs must be minimized. What configuration satisfies all three requirements?

A) Delta Sync Index, `pipeline_type="CONTINUOUS"`, Databricks-managed embeddings — continuous sync ensures near-real-time freshness, and Databricks-managed embeddings minimize per-query embedding computation time to achieve sub-50ms latency.
B) Delta Sync Index, `pipeline_type="TRIGGERED"` (triggered weekly), self-managed embeddings pre-computed in batch and stored in the Delta table, with a correctly sized Vector Search endpoint for the 8M embedding index — TRIGGERED aligns with weekly update frequency, self-managed batch embedding minimizes cost, and endpoint sizing handles the latency requirement.
C) Direct Vector Access Index with `pipeline_type="CONTINUOUS"` and self-managed real-time embeddings — the direct access API provides lower query latency than Delta Sync indexes, and continuous embedding updates ensure the index reflects the weekly knowledge base additions.
D) Delta Sync Index, `pipeline_type="TRIGGERED"`, Databricks-managed embeddings, with a single Small-tier Vector Search endpoint — the managed embedding model ensures consistent vector quality, and a single Small endpoint is sufficient for 8 million embeddings at sub-50ms latency.

**Correct Answer:** B
**Explanation:** B is correct. Matching requirements to configuration: (1) **< 50ms P95 latency** — achieved by correctly sizing the Vector Search endpoint (more nodes for a larger index) and using pre-computed self-managed embeddings (no embedding latency at query time — the query embedding is computed once and the ANN search runs against pre-indexed vectors). (2) **Updated once per week** — TRIGGERED mode is ideal; set up a weekly sync schedule. CONTINUOUS mode would waste compute resources running a persistent sync pipeline for a knowledge base that only changes weekly. (3) **Minimize embedding costs** — self-managed embeddings computed in batch (once per week on the new/changed chunks only) using cost-efficient batch processing is much cheaper than Databricks-managed embeddings which compute embeddings every time new data is written. A is wrong because CONTINUOUS sync wastes compute for a weekly-updated knowledge base, and Databricks-managed embeddings may not minimize cost for an 8M-chunk index. C is wrong because Direct Vector Access does not natively support CONTINUOUS sync — it requires manual embedding upload via API calls; and the combination described is not a valid architecture. D is wrong because a single Small-tier endpoint is likely insufficient for 8 million embeddings at sub-50ms P95 latency under concurrent query load — endpoint sizing must match the index size.
**Source:** Section 4: Assembling and Deploying – Objective 10: Configure vector search based on requirements — docs.databricks.com (search: "Mosaic AI Vector Search configuration" and "Vector Search endpoint sizing")

---

### Question 27
**Difficulty:** Advanced

A developer registers a model to Unity Catalog and then creates a Model Serving endpoint pointing to it. A week later, they need to update the underlying model (new version 2 registered). What is the zero-downtime upgrade process for the serving endpoint?

A) Delete the existing serving endpoint, create a new endpoint pointing to version 2, and update the application's endpoint URL — the brief downtime during endpoint creation is unavoidable for model version updates.
B) In the Model Serving UI or via REST API, add version 2 as a new served entity on the existing endpoint with a small traffic percentage (e.g., 10%), monitor its quality and latency metrics, then gradually shift traffic from version 1 to version 2 until version 2 receives 100% — then remove version 1 as a served entity.
C) Re-register version 1 in Unity Catalog with the same version number but updated model artifacts — MLflow will detect the artifact change and automatically hot-reload the serving endpoint within 2 minutes without downtime.
D) Create a Databricks Workflow that calls `mlflow.pyfunc.load_model()` on version 2 and assigns it to the endpoint's active model slot — the Workflow's model swap is atomic and provides zero-downtime switching.

**Correct Answer:** B
**Explanation:** B is correct. Databricks Model Serving supports traffic splitting between multiple model versions on the same endpoint — this is the canonical zero-downtime upgrade pattern (canary/blue-green deployment). The process: (1) Register model version 2 to Unity Catalog. (2) Via the Serving UI or REST API, add version 2 as a new served entity with a small traffic split (e.g., 10% to v2, 90% to v1). (3) Monitor v2's metrics (latency, error rate, quality from Inference Tables). (4) Gradually shift traffic: 25/75, 50/50, 75/25, 100/0. (5) Once 100% is on v2, remove v1. Throughout this process, at least one version is always serving — zero downtime. A is wrong because creating a new endpoint with downtime is the worst-case approach — traffic splitting avoids this entirely. C is wrong because MLflow model versions in Unity Catalog are immutable — you cannot update artifacts under the same version number; each change creates a new version. D is wrong because `mlflow.pyfunc.load_model()` is for loading models into Python code, not for configuring which version an active serving endpoint uses; endpoint model management is done via the Serving API.
**Source:** Section 4: Assembling and Deploying – Objective 7: Identify how to serve an LLM application — docs.databricks.com (search: "Databricks Foundation Model APIs" and "Provisioned throughput model serving")

---

### Question 28
**Difficulty:** Advanced

A developer builds a Streamlit app hosted on Databricks Apps that calls a Databricks Model Serving endpoint. When a user logs in to the App via SSO, they want the app to call the endpoint using the user's identity (not a Service Principal) so Unity Catalog access controls are enforced per-user. What authentication mechanism does Databricks Apps use to enable this?

A) Databricks Apps requires users to manually paste their personal access tokens (PAT) into the Streamlit app's sidebar input field, which the app stores in `st.session_state` and uses for all subsequent Model Serving API calls during the session.
B) Databricks Apps automatically provides the logged-in user's short-lived OAuth token to the application code via the Databricks SDK's `WorkspaceClient()` context, which the app uses to call the Model Serving endpoint on behalf of the authenticated user.
C) Databricks Apps creates a dedicated Service Principal for each user at login time, which makes all API calls on behalf of that user — the Service Principal is destroyed when the user session ends.
D) Databricks Apps uses anonymous pass-through authentication — the Model Serving endpoint receives calls without any user identity, and Unity Catalog applies workspace-level (not user-level) access controls to all app-originated requests.

**Correct Answer:** B
**Explanation:** B is correct. One of Databricks Apps' key architectural advantages is built-in SSO with identity pass-through. When a user authenticates to the Databricks App via SSO (Databricks identity), the App runtime automatically provides the authenticated user's OAuth token to the application code through the `WorkspaceClient()` context. The Streamlit app can then instantiate `WorkspaceClient()` without any manual credential configuration, and all API calls (to Model Serving endpoints, Unity Catalog, etc.) are made using the user's identity — meaning Unity Catalog row-level security, column masking, and model serving permissions are enforced per-user. A is wrong because requiring users to paste PATs is a security anti-pattern — Databricks Apps handles authentication automatically via SSO, eliminating the need for user-managed tokens. C is wrong because Databricks Apps does not create per-user Service Principals at login time — the user's own OAuth identity is passed through. D is wrong because Databricks Apps does not use anonymous authentication — a core value proposition is that user identity is preserved end-to-end for security and compliance.
**Source:** Section 4: Assembling and Deploying – Objective 15: Develop an appropriate interactive user-facing interface — docs.databricks.com (search: "Databricks Apps deploy agent")

---

### Question 29
**Difficulty:** Advanced

A team stores conversation history for a customer service agent in Lakebase using LangGraph's Checkpointer with `thread_id = user_session_id`. A user returns 3 days later and starts a new session. What happens to their previous conversation history, and how does the agent access it?

A) The previous conversation history is gone — LangGraph's Checkpointer only persists history within the same `thread_id` session, and once the session ends, all state is evicted from memory and is unrecoverable.
B) The previous conversation history is preserved in Lakebase (durable persistence). When the user starts a new session, the agent can either: (a) load the same `thread_id` to resume the exact previous conversation state, or (b) use a separate long-term memory Store to retrieve key facts from past sessions without loading the full history.
C) The previous conversation history is automatically deleted by Lakebase's 24-hour data retention policy — Lakebase is an in-memory cache, not a durable database, and all data is lost after the configured retention period expires.
D) The previous conversation history is preserved but requires a full table scan of the Lakebase conversation table because thread IDs are not indexed by default in Lakebase — performance degrades linearly with the number of past sessions stored.

**Correct Answer:** B
**Explanation:** B is correct. Lakebase is a fully managed, durable Postgres-compatible database — data persists indefinitely until explicitly deleted. LangGraph's Checkpointer writes conversation state (all message turns) to Lakebase keyed by `thread_id`. Because Lakebase is durable: (1) When the user returns 3 days later, all their previous conversation turns are still in Lakebase. (2) The agent can load the same `thread_id` to perfectly resume the conversation as if no time had passed (short-term continuity). (3) Alternatively, for cross-session learning, the agent can use LangGraph's Store API to write and retrieve key facts (preferences, unresolved issues) across sessions using a persistent user-keyed namespace. A is wrong because Lakebase is a durable database, not an in-memory session store — data persists across session endings; persistence is the entire reason for using Lakebase instead of in-memory storage. C is wrong because Lakebase is NOT an in-memory cache — it is a serverless managed Postgres database with standard database durability guarantees; there is no 24-hour retention policy. D is wrong because Postgres (which Lakebase is compatible with) supports indexed lookups — thread IDs can be indexed for O(log n) retrieval, not requiring a full table scan.
**Source:** Section 4: Assembling and Deploying – Objective 11: Configure a persistent datastore for memory — docs.databricks.com (search: "Agent memory Databricks" and "Lakebase Databricks Postgres")

---

### Question 30
**Difficulty:** Advanced

A developer writes a CI/CD test for their RAG chain component. They want to test the retriever independently (without calling the LLM) to verify that given a specific query, the correct documents are returned from Vector Search. What is the correct testing approach?

A) The retriever cannot be tested independently — because Vector Search is embedded within the LangChain chain, the only way to test it is to run the full end-to-end chain and check if the LLM's answer reflects the correct documents.
B) Instantiate the `DatabricksVectorSearch` retriever directly in the test, call `retriever.invoke("test query")`, and assert that the returned documents include the expected content — this tests the retriever in isolation without invoking the LLM or prompt template.
C) Use `mlflow.evaluate()` to test the retriever in isolation — pass the retriever as the `model` argument and provide the test query as the evaluation dataset; MLflow will run the retriever and return retrieval metrics.
D) Create a mock `DatabricksVectorSearch` retriever using Python's `unittest.mock` library and assert that `retriever.get_relevant_documents()` is called with the correct query — this validates the chain's retriever invocation without connecting to a real Vector Search index.

**Correct Answer:** B
**Explanation:** B is correct. LangChain's LCEL architecture makes components independently invokable. The `DatabricksVectorSearch` retriever implements LangChain's `BaseRetriever` interface with an `invoke()` method. In a unit or integration test, you can instantiate the retriever directly (pointing at the staging Vector Search index), call `retriever.invoke("What is the refund policy?")`, and assert properties of the returned document list — checking that the expected chunks are present, that the correct number of results was returned, and that metadata is correct. This is a true integration test of the retriever component without LLM involvement. A is wrong because the LCEL `|` operator creates composable, independently invokable components — each can be tested in isolation; testing only the full chain provides poor isolation when debugging retrieval failures. C is wrong because `mlflow.evaluate()` is for evaluating a complete model/chain against a quality benchmark dataset — it is not designed for unit testing a single retriever component in isolation. D is wrong because mocking the retriever only verifies that the chain CALLS the retriever, not that the retriever returns CORRECT results from a real Vector Search index — mocks are for unit tests of chain composition logic, not for verifying retrieval quality.
**Source:** Section 4: Assembling and Deploying – Objective 12: Apply CI/CD best practices — docs.databricks.com (search: "Databricks Asset Bundles CI/CD")

---

### Question 31
**Difficulty:** Advanced

A developer builds a Custom MCP Server using Databricks Apps and FastAPI. The server exposes two tools: `search_internal_docs()` and `submit_support_ticket()`. A Supervisor agent connects to it via the MCP protocol. What is a key advantage of hosting the Custom MCP Server on Databricks Apps versus a standalone external server?

A) Databricks Apps Custom MCP Servers automatically register their tools in Unity Catalog, making them discoverable by any agent in the workspace without requiring manual tool registration in the Supervisor's tool list.
B) Hosting on Databricks Apps keeps the Custom MCP Server within the Databricks security perimeter — it benefits from built-in SSO, Databricks identity, Unity Catalog access controls, and Unity AI Gateway governance for all tool invocations.
C) Databricks Apps Custom MCP Servers bypass the Unity AI Gateway and connect directly to the Supervisor agent's LangGraph runtime, eliminating the routing overhead that External MCP Servers incur through the Gateway.
D) Custom MCP Servers on Databricks Apps are co-located on the same compute cluster as the Model Serving endpoint, reducing network latency from the Supervisor to the MCP server to near-zero compared to external hosting.

**Correct Answer:** B
**Explanation:** B is correct. Hosting a Custom MCP Server on Databricks Apps provides all the governance and security benefits of the Databricks platform: (1) **SSO and Databricks identity** — users accessing tools via the MCP server are authenticated via Databricks identity, maintaining end-to-end audit trails. (2) **Unity Catalog access controls** — the MCP server can call Unity Catalog resources (Delta tables, ML models, Vector Search) using properly governed permissions. (3) **Unity AI Gateway** — all MCP traffic routes through the Gateway for rate limiting, cost monitoring, and compliance policies. (4) **No separate infrastructure** — no external server to deploy, scale, or secure separately. A is wrong because Custom MCP Server tools on Databricks Apps are NOT automatically registered in Unity Catalog — the Supervisor agent's tool list must be explicitly configured to point to the MCP server URL. C is wrong because Custom MCP Servers on Databricks Apps DO route through Unity AI Gateway — all MCP server traffic is governed through the Gateway, which is a feature (governance), not a limitation. D is wrong because Databricks Apps are not co-located on the same compute as Model Serving endpoints — they run on separate managed infrastructure; the latency benefit is not "near-zero" due to co-location.
**Source:** Section 4: Assembling and Deploying – Objective 13: Integrate managed, external, and custom MCP servers — docs.databricks.com (search: "MCP servers Databricks" and "Unity Catalog MCP services")

---

### Question 32
**Difficulty:** Advanced

A developer needs to add a Unity Catalog Function as a tool to a LangGraph agent. The function `main.agents.calculate_tax(amount DOUBLE, region STRING) RETURNS DOUBLE` is already registered. What is the correct Databricks SDK approach to make this function available as an LLM tool?

A) Import the function using `from databricks.sdk.service.catalog import FunctionAPI` and call `FunctionAPI.to_langchain_tool(function_name="main.agents.calculate_tax")` to get a LangChain-compatible tool object.
B) Use `UCFunctionToolkit` from `unitycatalog.ai.langchain` or the Databricks SDK's UC function toolkit — it automatically fetches the function's signature from Unity Catalog, creates a type-safe tool wrapper, and registers it with the LangGraph agent's tool list.
C) Convert the UC Function to a LangChain tool by manually writing a Python wrapper function with a matching signature, decorating it with `@tool`, and documenting its input/output schema in the docstring — Unity Catalog functions cannot be directly wrapped automatically.
D) Call the UC Function directly from inside a LangGraph node by executing `spark.sql("SELECT main.agents.calculate_tax(1000, 'CA')")` and return the Spark DataFrame result to the LLM as a JSON-serialized string.

**Correct Answer:** B
**Explanation:** B is correct. Databricks provides `UCFunctionToolkit` (available in the `unitycatalog-ai` package and Databricks SDK extensions) specifically for converting Unity Catalog Functions into LangChain-compatible tools. When initialized with a function name (e.g., `main.agents.calculate_tax`), `UCFunctionToolkit` automatically: (1) Fetches the function's metadata from Unity Catalog (parameter names, types, return type, description). (2) Creates a type-safe LangChain `Tool` object with the correct input schema. (3) Handles execution by calling the UC Function via the Databricks REST API when the LLM generates a tool call. The resulting tool can be added directly to a LangGraph agent's tool list. A is wrong because `FunctionAPI.to_langchain_tool()` is not a real method in the Databricks SDK — `UCFunctionToolkit` is the correct abstraction. C is wrong because manual wrapping with `@tool` is the pre-toolkit workaround — `UCFunctionToolkit` automates this completely, including type inference from the UC Function's registered schema. D is wrong because executing Spark SQL inside a LangGraph node and returning a raw DataFrame string is a fragile anti-pattern — it doesn't create a proper tool that the LLM's tool-calling interface can invoke through structured JSON.
**Source:** Section 4: Assembling and Deploying – Objective 13: Integrate managed, external, and custom MCP servers — docs.databricks.com (search: "MCP servers Databricks")

---

### Question 33
**Difficulty:** Advanced

A team wants to implement unit testing for their prompt template as part of their CI/CD pipeline, before deploying it to production. The prompt is registered in the MLflow Prompt Registry under the `staging` alias. How should the CI/CD test validate the prompt behavior before promoting to production?

A) Use `mlflow.load_prompt("prompts:/rag_prompt/staging")` in a pytest test to load the staging prompt, format it with test input variables, and use an LLM-as-a-judge or assertion-based check to verify the formatted prompt meets expected format and instruction quality.
B) The prompt cannot be unit tested independently — because prompts are natural language strings, behavioral validation requires a full MLflow evaluation run with the complete chain, not an isolated unit test.
C) Use `mlflow.compare_prompts(alias1="staging", alias2="production")` to run a built-in A/B comparison that automatically evaluates both prompt versions against a standard benchmark and returns a winner recommendation.
D) Unit test the prompt by checking that `mlflow.load_prompt("prompts:/rag_prompt/staging").text` is not equal to `mlflow.load_prompt("prompts:/rag_prompt/production").text` — confirming that the staging prompt is different from the current production version before promoting.

**Correct Answer:** A
**Explanation:** A is correct. The correct CI/CD approach for prompt validation is: (1) `mlflow.load_prompt("prompts:/rag_prompt/staging")` loads the staging prompt version. (2) Use the prompt's `.format()` or `.template` attribute to assemble test prompts with known test input variables. (3) Apply assertions to verify the formatted prompt: check that required variables are correctly substituted, that system instructions are present, that the format matches expected structure. (4) For higher-confidence validation, run the formatted prompt against an LLM on a small test set and use LLM-as-a-judge or regex-based checks to validate the output quality. This is a lightweight, fast test that can run in CI without a full `mlflow.evaluate()` cycle. B is wrong because prompts CAN be tested independently — at minimum, template formatting (variable substitution, structure) can be validated without any LLM call; and component-level testing is a CI/CD best practice. C is wrong because `mlflow.compare_prompts()` is not a real MLflow API function — prompt comparison in MLflow is done by loading and examining prompts in code, not via a built-in comparison API. D is wrong because checking that the prompts are merely DIFFERENT is a trivially weak test — it doesn't validate that the staging prompt is BETTER or even CORRECT; it would pass even if the staging prompt was accidentally emptied.
**Source:** Section 4: Assembling and Deploying – Objective 12 & 14: CI/CD best practices and prompt lifecycle — docs.databricks.com (search: "MLflow Prompt Registry aliases" and "Databricks Asset Bundles CI/CD")

---

### Question 34
**Difficulty:** Advanced

A developer reviews the following `ai_query()` usage in a Databricks SQL notebook:

```sql
SELECT
    id,
    ai_query(
        'databricks-meta-llama-3-70b-instruct',
        CONCAT('Extract the contract type from this text. Return only: NDA, SLA, MSA, or OTHER. Text: ', contract_text)
    ) AS contract_type
FROM main.legal.contracts
WHERE processed_date IS NULL;
```

What optimization issues, if any, exist with this query for a table with 500,000 unprocessed contracts?

A) No optimization issues — `ai_query()` automatically batches all 500,000 rows into optimal request sizes, parallelizes across serverless compute, and handles rate limiting internally; the query will complete efficiently.
B) The `CONCAT` function is a performance bottleneck — replacing it with a prepared statement parameter binding reduces SQL compilation overhead and improves throughput for large-scale `ai_query()` runs.
C) The query is missing a `LIMIT` clause — `ai_query()` on serverless SQL Warehouses requires a LIMIT to prevent runaway costs; without a LIMIT, the query will fail with a budget exceeded error after processing 10,000 rows.
D) The prompt includes the full contract text inline which could exceed the model's context window for very long contracts — the developer should add a `LENGTH(contract_text) < 10000` filter or apply pre-processing to truncate or summarize long contracts before `ai_query()` classification.

**Correct Answer:** D
**Explanation:** D is correct. The most significant issue is that `contract_text` is passed directly without any length guard. Legal contracts can be thousands or tens of thousands of words long. If any contract's text (plus the prompt prefix) exceeds the LLM's context window, the `ai_query()` call for that row will fail — causing the entire query to fail or producing NULL results for those rows. Best practices include: adding a `LENGTH(contract_text) < <token_limit_estimate>` filter, or using a pre-processing step to extract the first N characters of the contract header for classification (contracts often have their type identified early). A is wrong because while `ai_query()` does parallelize and handle rate limiting, it does NOT handle context window overflows — rows that exceed the context window will generate errors, not gracefully truncate. B is wrong because `CONCAT` is a standard SQL string function with negligible overhead compared to model inference time — it is not a performance bottleneck in this context. C is wrong because `ai_query()` does not require a `LIMIT` clause and will not fail with a budget error after 10,000 rows — it processes all qualifying rows; budget controls are managed through Unity AI Gateway cost budgets, not query-level LIMIT constraints.
**Source:** Section 4: Assembling and Deploying – Objective 9: Identify batch inference workloads and apply ai_query() — docs.databricks.com (search: "ai_query function Databricks SQL" and "Batch inference AI functions")

---

### Question 35
**Difficulty:** Proficiency

A principal engineer designs a complete deployment architecture for a RAG application on Databricks. They must satisfy: (1) vector search updates must reflect new documents within 5 minutes of them being added to the source Delta table, (2) the serving endpoint must never store credentials in plain text, (3) the application must be accessible to employees via their existing company SSO without separate login, (4) infrastructure must be version-controlled and reproducible across dev/staging/prod. Map each requirement to the correct Databricks feature.

A) (1) VS CONTINUOUS sync → (2) Databricks Secrets as environment variables → (3) Databricks Apps with built-in SSO → (4) Databricks Asset Bundles in Git.
B) (1) VS TRIGGERED sync triggered every 5 minutes → (2) Unity Catalog column encryption → (3) External web app with OAuth M2M → (4) Databricks Workflows deployment notebook.
C) (1) VS CONTINUOUS sync → (2) Unity Catalog row-level security → (3) Genie app for Teams → (4) MLflow Projects.
D) (1) VS TRIGGERED sync → (2) Databricks Secrets in `load_context()` → (3) Databricks Apps → (4) Delta Live Tables pipeline YAML.

**Correct Answer:** A
**Explanation:** A is correct. Each requirement maps precisely: (1) **< 5 minutes freshness** → `pipeline_type="CONTINUOUS"` on the Vector Search Delta Sync index monitors the source Delta table's CDF in near real-time (typical lag < 1–2 minutes) — well within the 5-minute requirement. TRIGGERED sync requires manual triggers and cannot guarantee sub-5-minute freshness. (2) **No plain-text credentials** → Databricks Secrets Scope stores credentials encrypted; referencing them as environment variables in the endpoint configuration means the values are never visible in code, logs, or notebook cells. (3) **Company SSO without separate login** → Databricks Apps integrates with Databricks workspace SSO — employees log in with their existing company identity (via SAML/OIDC), with no separate password or registration. (4) **Version-controlled reproducible infrastructure** → Databricks Asset Bundles (DABs) define all Databricks resources in `databricks.yml` committed to Git, enabling `databricks bundle deploy` to reproduce the exact same infrastructure across dev/staging/prod. B is wrong because TRIGGERED every 5 minutes cannot guarantee sub-5-minute freshness (sync takes time after triggering), Unity Catalog column encryption is for data governance not credential management, and Workflows notebooks are not IaC. C and D have partial matches but contain incorrect mappings for multiple requirements.
**Source:** Section 4: Assembling and Deploying – Objectives 2, 6, 10, 12, 15 — docs.databricks.com (search: "Databricks Asset Bundles CI/CD" and "Mosaic AI Vector Search configuration" and "Databricks Secrets model serving")

---

### Question 36
**Difficulty:** Proficiency

A developer receives this error when registering an MLflow model to Unity Catalog:

```
MlflowException: Model 'main.ml_models.rag_chain' requires a model signature.
Provide an input_example or explicitly define a signature using mlflow.models.infer_signature().
```

The model was logged with:
```python
mlflow.langchain.log_model(lc_model=chain, artifact_path="rag_chain")
```

What is the MINIMUM fix, and what two alternative approaches exist?

A) The minimum fix is to add `registered_model_name="main.ml_models.rag_chain"` to the `log_model()` call — the registration error occurs because the model name was not specified at log time, causing MLflow to attempt registration without namespace context.
B) Minimum fix: Add `input_example={"question": "What is the return policy?", "context": "Our return policy..."}` to `log_model()` — MLflow automatically infers the signature from this example. Alternative 1: Manually create a signature with `infer_signature(inputs, outputs)` and pass it to `log_model(signature=...)`. Alternative 2: Call `mlflow.models.add_signature(model_uri, signature)` to add a signature to an already-logged model without re-logging.
C) Minimum fix: Run `mlflow.set_registry_uri("databricks-uc")` before the `log_model()` call — the error occurs because Unity Catalog's registry is not selected and the model was sent to the legacy registry which rejects signatures.
D) The error cannot be fixed without deleting the current model version and re-running the full training and evaluation pipeline — model signatures cannot be added retrospectively to logged MLflow models in Unity Catalog.

**Correct Answer:** B
**Explanation:** B is correct. Three approaches to fix the signature error: (1) **Minimum fix** — Add `input_example={...}` to `mlflow.langchain.log_model()`. MLflow 2.5+ automatically infers the model signature from the provided example (inspecting its data types and column names) and attaches it to the model artifact. This is the recommended approach for its simplicity. (2) **Alternative 1** — Explicitly define the signature by running the chain on sample data, capturing inputs and outputs, and using `mlflow.models.infer_signature(model_input=sample_input, model_output=sample_output)`, then pass it as `log_model(signature=signature)`. (3) **Alternative 2** — Use `mlflow.models.add_signature(model_uri="runs:/<run_id>/rag_chain", signature=signature)` to attach a signature to an ALREADY-LOGGED model without re-running `log_model()`. A is wrong because `registered_model_name` specifies where to register the model, not what signature it has — adding this parameter does not fix the missing signature. C is wrong because `mlflow.set_registry_uri("databricks-uc")` is needed to point to Unity Catalog, but the error is specifically about the missing signature, not registry selection. D is wrong because signatures CAN be added to already-logged models using `mlflow.models.add_signature()` — no re-logging is required.
**Source:** Section 4: Assembling and Deploying – Objective 5: Register the model to Unity Catalog using MLflow — docs.databricks.com (search: "Register model Unity Catalog MLflow" and "MLflow model signature input example")

---

### Question 37
**Difficulty:** Proficiency

An enterprise runs a RAG-based legal research assistant used by 500 attorneys. Requirements: (1) each attorney's search results must only include documents they are individually authorized to see (row-level security on the knowledge base), (2) the agent must remember each attorney's practice area from the last session, (3) new case law documents must be indexed within 2 hours of being added, (4) the application must run within the corporate IT security perimeter without external SaaS dependencies. Design the architecture.

A) Vector Search Direct Access Index (for row-level security at query time) + Lakebase (cross-session attorney memory) + TRIGGERED sync triggered every 90 minutes (meets 2-hour freshness) + Databricks Apps (within the Databricks security perimeter).
B) Vector Search Delta Sync Index with CONTINUOUS sync + Unity Catalog row-level security on the source Delta table (access filters propagate to Vector Search queries) + Lakebase Store for cross-session memory + Databricks Apps for the front-end within the Databricks security perimeter.
C) External Elasticsearch cluster for row-level security + Redis for session memory + CONTINUOUS sync from Delta to Elasticsearch + Databricks Model Serving for the LLM component — this provides enterprise-grade security without relying on Databricks-native components.
D) Vector Search Delta Sync Index with CONTINUOUS sync + no memory (each attorney re-enters their practice area per session, as Databricks does not support cross-session agent memory within the security perimeter) + Databricks Apps front-end.

**Correct Answer:** B
**Explanation:** B is correct. Mapping requirements: (1) **Row-level security per attorney** → Unity Catalog row-level security policies on the source Delta table are propagated to Vector Search queries via the `filters` parameter in `similarity_search()`. The searching identity (attorney's UC identity) determines which rows they can retrieve — documents outside their authorization are excluded at the Vector Search layer. (2) **Cross-session memory** → LangGraph Store API writing attorney practice area preferences to Lakebase, keyed by attorney user ID. (3) **< 2-hour freshness** → CONTINUOUS sync ensures documents are indexed within minutes of being added — well within 2 hours. (4) **Within security perimeter** → Databricks Apps (built-in SSO, UC identity, within Databricks perimeter). A is wrong because a Direct Vector Access Index doesn't natively propagate Unity Catalog row-level security — the security controls are at the Unity Catalog source table, not at the index query level; also TRIGGERED at 90 minutes is a compromise when CONTINUOUS is more reliable. C is wrong because using Elasticsearch and Redis introduces external SaaS dependencies, violating requirement 4 (within corporate IT perimeter). D is wrong because Databricks does support cross-session memory via Lakebase — omitting memory is not a technical limitation but an architectural choice that directly violates requirement 2.
**Source:** Section 4: Assembling and Deploying – Objectives 6, 8, 10, 11, 15 — docs.databricks.com (search: "Mosaic AI Vector Search configuration" and "Agent memory Databricks" and "Databricks Apps deploy agent")

---

### Question 38
**Difficulty:** Proficiency

A data engineer implements batch inference using `ai_query()` on 2 million product descriptions to extract structured JSON attributes. The query works on a 1,000-row sample but fails on the full 2 million rows with `ModelNotAvailableException: Rate limit exceeded` errors. What is the correct remediation?

A) Switch to a Provisioned Throughput endpoint with enough token-per-second capacity to handle the 2 million rows within the SQL query's timeout window — Provisioned Throughput eliminates rate limiting by dedicating capacity to your workload.
B) Add a `WHERE MOD(id, 4) = 0` clause to the SQL query to process only 25% of the rows in the current run, then run the query 4 times with different modulus values to process all rows while staying within rate limits.
C) Split the query into 2,000 separate SQL queries of 1,000 rows each using a Databricks Workflow with 2,000 Tasks, which distributes the load across 2,000 separate rate limit windows and avoids the per-minute token limit.
D) Increase the serverless SQL Warehouse's concurrency setting from 1 to 10, which allows 10 parallel `ai_query()` executions per row and reduces the wall-clock time by 10×, staying within the model endpoint's rate limit per request.

**Correct Answer:** A
**Explanation:** A is correct. The `Rate limit exceeded` error when scaling from 1K to 2M rows indicates that the pay-per-token endpoint's rate limit (requests per minute or tokens per minute) is being hit. The correct solution for production-scale batch inference is to use a Provisioned Throughput endpoint with capacity sized for the workload. Provisioned Throughput reserves a dedicated tokens-per-second (TPS) allocation — there is no throttling for traffic within the reserved capacity. The team should: (1) estimate total tokens needed (2M rows × avg tokens per row), (2) calculate required TPS to complete within the batch window, (3) provision the endpoint with that TPS. B is wrong because processing in 4 separate runs via modulus is a workaround that doesn't fix the underlying rate limit — each run still hits the same rate limit. C is wrong because 2,000 separate Workflow Tasks each running 1K-row queries doesn't avoid the rate limit — each task still calls the same endpoint, and 2,000 concurrent tasks would hit the rate limit faster, not slower. D is wrong because the warehouse concurrency setting controls how many SQL queries run simultaneously on the warehouse — it doesn't divide the rate limit; increasing concurrency actually INCREASES the rate of API calls, worsening the rate limit problem.
**Source:** Section 4: Assembling and Deploying – Objective 9: Identify batch inference workloads and apply ai_query() — docs.databricks.com (search: "ai_query function Databricks SQL" and "Batch inference AI functions")

---

### Question 39
**Difficulty:** Proficiency

A developer builds a sophisticated pyfunc model with pre-processing (input schema validation, PII sanitization) and post-processing (JSON parsing, confidence threshold filtering). During load testing, they discover that 12% of requests return incorrect results when inputs contain Unicode special characters (emoji, non-ASCII). Where in the pyfunc implementation should the Unicode normalization fix be applied?

A) In `load_context()` — because Unicode normalization is a one-time configuration operation that sets the encoding context for all subsequent `predict()` calls, and it should be performed during the model's initialization phase.
B) In the `_preprocess()` method called from `predict()` — because normalization must be applied to each individual inference request's input before the model call, and the `_preprocess()` step is exactly where per-request input transformations belong.
C) In the MLflow model signature definition using `ColSpec(type=DataType.binary)` — declaring the input column as binary type forces MLflow to accept raw bytes and skip Unicode decoding, preventing the encoding issue before it reaches `predict()`.
D) In the Model Serving endpoint's environment variable configuration using `PYTHONIOENCODING=utf-8` — setting the encoding environment variable makes all Python string operations in the serving container default to UTF-8, automatically fixing Unicode handling without code changes.

**Correct Answer:** B
**Explanation:** B is correct. The `_preprocess()` method (or equivalently, the first lines of `predict()`) is the correct location for per-request input transformations — including Unicode normalization. Each request's input passes through `_preprocess()` before reaching the model, so normalization applied here ensures all model calls receive clean, normalized text. The typical fix: `import unicodedata; text = unicodedata.normalize('NFC', text)` applied to each input string. A is wrong because `load_context()` runs once at startup and does not have access to individual request data — you can load a Unicode normalizer object there, but you cannot normalize the per-request inputs in `load_context()`. C is wrong because changing the input signature to binary type forces callers to pre-encode strings as bytes — this is an API-breaking change that shifts the burden to callers and does not actually fix the normalization issue within the model. D is wrong because `PYTHONIOENCODING=utf-8` affects stdin/stdout encoding for the Python process — it does not automatically normalize Unicode characters in string variables; normalization (NFC, NFKC) is distinct from encoding and must be explicitly applied in code.
**Source:** Section 4: Assembling and Deploying – Objective 1: Code a chain using a pyfunc model with pre- and post-processing — docs.databricks.com (search: "mlflow.pyfunc PythonModel custom" and "Deploy custom Python model Databricks Model Serving")

---

### Question 40
**Difficulty:** Proficiency

A team's production RAG agent has been running for 6 months. A new regulation requires that all documents tagged with `classification = "confidential"` must never be retrievable by any user through the Vector Search index. The index currently contains 500,000 documents, of which 50,000 are newly classified as confidential. What is the correct remediation?

A) Delete the confidential documents from the source Delta table, then trigger a full re-index of the Vector Search index — the full re-index rebuilds the index from scratch, ensuring the confidential document vectors are permanently removed.
B) Update the source Delta table to remove the 50,000 confidential rows (using `DELETE FROM ... WHERE classification = "confidential"`), apply the `VACUUM` command to remove the underlying Parquet files, trigger a Vector Search sync — the sync processes the CDF delete operations and removes the corresponding vectors from the index.
C) Add a `filter = "classification != 'confidential'"` metadata filter to all `similarity_search()` calls in the retriever code — this filter prevents confidential documents from being returned by queries even though their vectors remain indexed.
D) Assign a Unity Catalog row-level security policy that blocks the `databricks-vector-search` service principal from reading confidential rows — this prevents the Vector Search service from indexing or returning the confidential document vectors.

**Correct Answer:** B
**Explanation:** B is correct — and order matters. The correct sequence is: (1) `DELETE FROM main.schema.chunked_docs WHERE classification = 'confidential'` — removes the rows from the source Delta table (creates DELETE entries in the CDF). (2) `VACUUM main.schema.chunked_docs` (after removing the 7-day default retention) — physically deletes the underlying Parquet files so the confidential text is not in storage. (3) Trigger a Vector Search sync (`index.sync()` or automatic via CONTINUOUS mode) — the sync processes the CDF DELETE operations and removes the corresponding vector entries from the index. This fully eliminates the confidential vectors. A is wrong because a "full re-index from scratch" is expensive and slower than incremental CDF-based sync for 50,000 deleted rows — and more importantly, VACUUM is still needed to remove the underlying Parquet files. C is wrong because filtering at query time leaves the confidential vectors IN the index — a compromised or incorrectly implemented filter could expose them; true remediation requires removing the vectors from the index, not just filtering results. D is wrong because row-level security on the `databricks-vector-search` service principal would prevent future sync of those rows, but doesn't remove the vectors already indexed — the 50,000 existing vectors remain searchable.
**Source:** Section 4: Assembling and Deploying – Objective 6 & 8: Create/query Vector Search index and key concepts — docs.databricks.com (search: "Create Mosaic AI Vector Search index" and "Mosaic AI Vector Search overview")
