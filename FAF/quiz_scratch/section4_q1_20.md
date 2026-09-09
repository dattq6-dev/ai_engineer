### Question 1
**Difficulty:** Beginner

A developer wants to wrap a custom Python inference function — including input validation and output formatting — as a deployable MLflow model. Which MLflow class should they subclass?

A) `mlflow.sklearn.SklearnModel` — because all Python-based ML models in Databricks must extend the scikit-learn base class to enable automatic serialization and deserialization during serving.
B) `mlflow.pyfunc.PythonModel` — because it is MLflow's generic Python function wrapper that lets you implement any custom pre-processing, model call, and post-processing logic inside `load_context()` and `predict()` methods.
C) `mlflow.langchain.LangChainModel` — because Databricks requires all custom Python chains to inherit from the LangChain model base class to ensure compatibility with the Model Serving endpoint runtime.
D) `mlflow.models.BaseModel` — because all custom MLflow models must extend `BaseModel` as the root class, with specialized flavors like pyfunc or sklearn registered as plugins that extend this root class.

**Correct Answer:** B
**Explanation:** B is correct. `mlflow.pyfunc.PythonModel` is MLflow's generic "Python function" base class for creating fully custom model wrappers. You subclass it and implement `load_context()` (for one-time initialization at endpoint startup) and `predict()` (for per-request inference with any custom pre/post-processing logic). It is the correct tool when standard framework flavors (LangChain, sklearn) don't provide sufficient control. A is wrong because `mlflow.sklearn` is for scikit-learn estimators implementing `fit()`/`predict()` — custom Python chains are not scikit-learn estimators and cannot be logged with this flavor. C is wrong because there is no `mlflow.langchain.LangChainModel` base class to subclass — LangChain models are logged using `mlflow.langchain.log_model()` directly, not via subclassing. D is wrong because `mlflow.models.BaseModel` does not exist as a user-subclassable class in MLflow's public API — the correct base class for custom Python models is `mlflow.pyfunc.PythonModel`.
**Source:** Section 4: Assembling and Deploying – Objective 1: Code a chain using a pyfunc model with pre- and post-processing — docs.databricks.com (search: "mlflow.pyfunc PythonModel custom")

---

### Question 2
**Difficulty:** Beginner

A production Model Serving endpoint was created under a developer's personal user account. The developer leaves the company, and their account is deactivated. What happens to the endpoint's access to Unity Catalog resources?

A) The endpoint continues to operate normally because Databricks Model Serving endpoints use anonymous compute identities that are independent of the creator's user account after deployment.
B) The endpoint loses access to Unity Catalog resources (Delta tables, UC Functions, Vector Search indexes) because the endpoint's data access identity is permanently bound to the creator's account, which is now inactive.
C) The endpoint automatically migrates to the workspace admin's identity, inheriting the admin's Unity Catalog permissions and continuing to operate with full access to all resources.
D) The endpoint enters a read-only mode, allowing existing cached embeddings to be served but blocking any new Delta table reads or Vector Search queries until a new creator account is assigned.

**Correct Answer:** B
**Explanation:** B is correct. In Databricks Model Serving, the endpoint's Unity Catalog data access identity is permanently bound to the identity of the user who CREATED the endpoint. When that user's account is deactivated, the endpoint can no longer authenticate to Unity Catalog resources (Delta tables, UC Functions, Vector Search indexes) — causing runtime errors during inference. This is exactly why Databricks best practices mandate creating production endpoints under a dedicated Service Principal (a non-human machine account) rather than a personal user account — Service Principals are not tied to individual employees. A is wrong because Model Serving endpoints are not anonymous — they use the creator's identity for all data access operations. C is wrong because Databricks does not automatically migrate the endpoint's identity to a workspace admin — identity migration requires explicit reconfiguration. D is wrong because there is no "read-only mode" in Model Serving — the endpoint either succeeds or fails its data access calls based on the creator's permissions.
**Source:** Section 4: Assembling and Deploying – Objective 2: Control access to resources from model serving endpoints — docs.databricks.com (search: "Model serving endpoint permissions Databricks")

---

### Question 3
**Difficulty:** Beginner

A developer builds a simple RAG chain using LangChain: `chain = prompt | llm | output_parser`. They want to log it to MLflow for deployment. Which logging function is most appropriate for this standard LangChain chain?

A) `mlflow.pyfunc.log_model(python_model=CustomClass())` — because all Databricks deployable chains must be wrapped in a custom `PythonModel` class to provide the serving runtime with the necessary metadata.
B) `mlflow.langchain.log_model(lc_model=chain, artifact_path="chain", input_example={...})` — because it natively serializes LangChain chains (including LCEL runnables) with automatic dependency detection and signature inference.
C) `mlflow.sklearn.log_model(sk_model=chain, artifact_path="chain")` — because LangChain's `|` pipe operator is equivalent to scikit-learn's `Pipeline`, making the sklearn flavor compatible with LangChain chains.
D) `mlflow.spark.log_model(spark_model=chain, artifact_path="chain")` — because LangChain chains run on Spark executors in Databricks and must be serialized with the Spark MLflow flavor to ensure distributed execution compatibility.

**Correct Answer:** B
**Explanation:** B is correct. `mlflow.langchain.log_model()` is the designated MLflow flavor for logging LangChain chains and LCEL runnables. It handles automatic serialization of the chain, detects Python package dependencies, and infers the model signature from the `input_example`. This is the standard, simplest approach for deploying a standard LangChain chain — no custom wrapping required. A is wrong because `mlflow.pyfunc.log_model()` with a custom `PythonModel` class is for complex custom logic that goes beyond standard LangChain chains — using it for a simple `prompt | llm | parser` chain adds unnecessary boilerplate. C is wrong because scikit-learn's `Pipeline` and LangChain's `|` LCEL operator are unrelated — LangChain chains implement different interfaces and cannot be serialized with the sklearn flavor. D is wrong because LangChain chains run on the driver node as Python code, not on Spark executors as distributed ML models; the Spark MLflow flavor is for Spark ML pipelines, not LangChain.
**Source:** Section 4: Assembling and Deploying – Objective 3: Code a simple chain according to requirements — docs.databricks.com (search: "Log and load LangChain models MLflow Databricks")

---

### Question 4
**Difficulty:** Beginner

When registering an MLflow model to Unity Catalog, what naming convention must the model name follow?

A) The model name must be a simple string with no dots or slashes (e.g., `rag_app_v2`), and Unity Catalog automatically assigns it to the default catalog and schema of the current workspace.
B) The model name must follow the three-level namespace `catalog.schema.model_name` (e.g., `main.my_schema.rag_app`) to specify exactly which Unity Catalog location owns and governs the model.
C) The model name must follow the format `workspace_id/experiment_id/model_name` to link the Unity Catalog model to its originating MLflow experiment run for full lineage tracking.
D) The model name must be prefixed with `uc://` (e.g., `uc://main.my_schema.rag_app`) to signal to MLflow that the target registry is Unity Catalog rather than the default MLflow Model Registry.

**Correct Answer:** B
**Explanation:** B is correct. Unity Catalog uses a three-level namespace for all objects: `catalog.schema.object_name`. When registering a model to Unity Catalog, the `registered_model_name` parameter must follow this convention (e.g., `"main.my_schema.rag_app"`). This determines which catalog and schema governs the model — controlling permissions, lineage tracking, and discoverability. A is wrong because a flat name without dots would attempt to register to the legacy MLflow Model Registry (if `mlflow.set_registry_uri("databricks-uc")` is not set), not to Unity Catalog; Unity Catalog always requires the three-level namespace. C is wrong because the workspace/experiment IDs are not part of the model registration name — MLflow automatically tracks lineage from the originating run; the model name is just the Unity Catalog three-level reference. D is wrong because there is no `uc://` prefix convention in MLflow model registration — the Unity Catalog registry is selected by calling `mlflow.set_registry_uri("databricks-uc")` before registration, not by prefixing the model name.
**Source:** Section 4: Assembling and Deploying – Objective 5: Register the model to Unity Catalog using MLflow — docs.databricks.com (search: "Register model Unity Catalog MLflow")

---

### Question 5
**Difficulty:** Beginner

What is the purpose of the `load_context()` method in an `mlflow.pyfunc.PythonModel` subclass?

A) `load_context()` is called on every inference request to reload the model's context (retrieved documents, conversation history) from the latest state in the database, ensuring each prediction uses fresh data.
B) `load_context()` is called once when the Model Serving endpoint starts up, and is used to load heavy objects like LLM clients, tokenizers, or configuration files that should be initialized once and reused across all requests.
C) `load_context()` loads the MLflow model's input example and signature from the artifact store and validates that each incoming request matches the expected schema before passing it to `predict()`.
D) `load_context()` registers the model's dependencies with the Databricks serving runtime at startup, downloading and installing any Python packages listed in `pip_requirements` that are not already available in the serving environment.

**Correct Answer:** B
**Explanation:** B is correct. `load_context()` runs exactly once when the Model Serving endpoint initializes (cold start). Its purpose is to perform expensive one-time initialization — creating LLM API clients, loading tokenizers, reading configuration files, connecting to Vector Search — so these resources are ready and reused across all subsequent requests without being re-initialized per request. This dramatically reduces per-request latency. A is wrong because `load_context()` is NOT called on every request — it is called only once at startup. Reloading context per-request would be the correct description of accessing session state within `predict()`. C is wrong because signature and input example validation is handled by MLflow's serving framework automatically — `load_context()` is for user-defined initialization code, not MLflow's internal validation logic. D is wrong because Python package installation from `pip_requirements` is handled by the MLflow serving runtime during environment setup, not within `load_context()` — the method runs after the environment is already set up.
**Source:** Section 4: Assembling and Deploying – Objective 1: Code a chain using a pyfunc model — docs.databricks.com (search: "mlflow.pyfunc PythonModel custom")

---

### Question 6
**Difficulty:** Beginner

A developer calls `vsc.create_delta_sync_index()` with `pipeline_type="TRIGGERED"`. Three hours later, 500 new document chunks are appended to the source Delta table. Will those new chunks be searchable in the Vector Search index immediately?

A) Yes — Delta Sync indexes with `TRIGGERED` mode monitor the source Delta table's transaction log in real time and automatically index new rows within 30 seconds of the APPEND operation completing.
B) No — `TRIGGERED` mode only syncs when explicitly triggered by calling `index.sync()` via the SDK or REST API. Until a sync is triggered, the 500 new chunks are invisible to the Vector Search index.
C) Yes — Delta Lake's ACID transaction guarantees mean that any committed row in the source Delta table is immediately queryable through the Vector Search index, regardless of the sync pipeline type configuration.
D) No — new rows are only indexed during the nightly Databricks Vector Search maintenance window that runs at 2:00 AM UTC, regardless of whether `TRIGGERED` or `CONTINUOUS` sync mode is configured.

**Correct Answer:** B
**Explanation:** B is correct. `TRIGGERED` pipeline mode means the Vector Search index does NOT automatically detect and propagate changes from the source Delta table. It only updates when a sync is explicitly initiated — either by calling `index.sync()` programmatically via the Python SDK, via the Databricks REST API, or through the Databricks UI's "Sync now" button. Until that manual trigger fires, the 500 new chunks exist in the Delta table but are completely invisible to the Vector Search index. A is wrong because real-time automatic monitoring is the behavior of `CONTINUOUS` mode, not `TRIGGERED` mode — confusing these two modes is a common exam trap. C is wrong because Delta ACID guarantees apply to the source Delta table's consistency, not to the derived Vector Search index — the index is a separate derived artifact that must be explicitly synchronized. D is wrong because there is no automatic nightly maintenance window for Vector Search sync — all syncs in `TRIGGERED` mode are explicitly user-initiated.
**Source:** Section 4: Assembling and Deploying – Objective 6: Create and query a Vector Search index — docs.databricks.com (search: "Create Mosaic AI Vector Search index")

---

### Question 7
**Difficulty:** Beginner

What is the key difference between Databricks Foundation Model API's "Pay-per-token" mode and "Provisioned Throughput" mode?

A) Pay-per-token uses cloud GPU instances managed by the customer, while Provisioned Throughput uses Databricks-managed serverless GPUs — the difference is who manages the underlying hardware infrastructure.
B) Pay-per-token is serverless (no capacity reservation) with per-token billing — best for prototyping and variable workloads. Provisioned Throughput reserves a guaranteed tokens-per-second capacity — required for production SLAs, compliance, and fine-tuned models.
C) Pay-per-token only supports Llama-3 family models, while Provisioned Throughput supports any open-source model including Mistral, Mixtral, and CodeLlama, giving broader model selection flexibility.
D) Pay-per-token charges for both input and output tokens, while Provisioned Throughput charges only for output tokens since the input is processed by a shared embedding cache that amortizes input token costs.

**Correct Answer:** B
**Explanation:** B is correct. The fundamental difference is capacity management: Pay-per-token is a shared, serverless pool with no capacity reservation — you pay for exactly what you use, there's no latency guarantee, and it may throttle under high load. This makes it ideal for development and low-volume prototyping. Provisioned Throughput reserves a dedicated number of tokens-per-second (TPS), guaranteeing that capacity regardless of other traffic — essential for production applications with latency SLAs, for HIPAA-compliant workloads requiring dedicated compute, and for deploying custom fine-tuned models. A is wrong because both modes run on Databricks-managed infrastructure — the customer doesn't manage GPUs in either case; the difference is capacity reservation, not infrastructure ownership. C is wrong because Pay-per-token supports multiple model families (Llama, Mistral, Mixtral, DBRX), not just Llama-3; and Provisioned Throughput also supports these models plus custom fine-tuned versions. D is wrong because both modes charge for input and output tokens — there is no "input caching" pricing mechanism that eliminates input token charges for Provisioned Throughput.
**Source:** Section 4: Assembling and Deploying – Objective 7: Identify how to serve an LLM application that leverages Foundation Model APIs — docs.databricks.com (search: "Databricks Foundation Model APIs")

---

### Question 8
**Difficulty:** Beginner

A team wants to run sentiment classification on 5 million customer reviews stored in a Delta table as a nightly batch job. Which Databricks tool is most appropriate?

A) LangChain with a `ChatDatabricks` LLM and a Python `for` loop that iterates over each review row in a Spark DataFrame, calling the LLM API once per row and writing results back to a new Delta column.
B) A LangGraph agent with a classification node that processes each review as a separate conversation turn, maintaining sentiment state across the full 5 million review dataset.
C) Databricks `ai_query()` SQL function in a serverless SQL warehouse query that selects all 5 million rows and applies the classification in a single SQL statement, letting Databricks parallelize across executors automatically.
D) A Databricks Workflow with 5 million individual Tasks — one per review — each calling a Foundation Model API REST endpoint, scheduled to complete before the morning business hours begin.

**Correct Answer:** C
**Explanation:** C is correct. `ai_query()` is Databricks' batch inference tool: it allows you to apply a model to every row of a Delta table in a single SQL query. The serverless SQL warehouse automatically parallelizes the inference calls across its executors, handles rate-limit retries, and processes millions of rows efficiently without any custom orchestration code. A is wrong because a Python `for` loop over 5 million rows is sequential — it processes one review at a time, would take hours or days, and misses all of Databricks' native parallelization capabilities. B is wrong because LangGraph is for stateful, multi-step reasoning agents — using it to classify 5 million independent reviews with no inter-row state adds extreme orchestration overhead for a task that is trivially addressed by `ai_query()`. D is wrong because creating 5 million Workflow Tasks is computationally absurd — Databricks Workflows are designed for dozens to hundreds of tasks representing pipeline stages, not one task per data row.
**Source:** Section 4: Assembling and Deploying – Objective 9: Identify batch inference workloads and apply ai_query() — docs.databricks.com (search: "ai_query function Databricks SQL")

---

### Question 9
**Difficulty:** Beginner

A team uses the MLflow Prompt Registry to manage their RAG system prompt. They have the prompt registered as version 1 (dev), version 2 (staging), and version 3 (production). The application code loads the prompt using `mlflow.load_prompt("prompts:/support_prompt/production")`. What does "promoting" the prompt to a new version involve?

A) Rewriting the application code to change the version number from `"production"` to a new integer (e.g., `"prompts:/support_prompt/4"`), then redeploying the serving endpoint with the updated code pointing to version 4.
B) Re-assigning the `production` alias in the MLflow Prompt Registry to point to the new (validated) prompt version — the application code remains unchanged because it loads by alias (`"production"`), not by version number.
C) Creating a new MLflow experiment run with the new prompt version as a run parameter, then updating the model serving endpoint to load from the latest experiment run ID rather than the prompt registry alias.
D) Deleting the current `production` alias from version 3 in the Registry, creating a new `production_v4` alias on the new version, and updating the application code to reference the new alias name.

**Correct Answer:** B
**Explanation:** B is correct. This is the core benefit of prompt aliases in the MLflow Prompt Registry. The application code references the prompt by a mutable alias (`"production"`) — not by an immutable version number. When a new prompt version is validated and ready for production, the team re-assigns the `production` alias to point to the new version. Because the application code always loads `"prompts:/support_prompt/production"`, it automatically picks up the newly aliased version WITHOUT any code change or redeployment. This is the prompt equivalent of a blue-green deployment — zero-downtime promotion with full version history preserved. A is wrong because changing the version number in application code requires a code change and redeployment — this defeats the purpose of using aliases (which eliminate the need for code changes during promotion). C is wrong because experiment run IDs are for model and metric tracking, not for prompt version promotion — the Prompt Registry's alias system handles this more cleanly. D is wrong because creating a new alias name (`production_v4`) still requires updating the application code to reference the new alias — this negates the alias benefit. The correct pattern is to reuse the same `production` alias name while updating which version it points to.
**Source:** Section 4: Assembling and Deploying – Objective 14: Apply prompt version control and manage prompt lifecycle — docs.databricks.com (search: "MLflow Prompt Registry Databricks")

---

### Question 10
**Difficulty:** Beginner

An internal analytics team wants business users to query their company's sales data using natural language from within Microsoft Teams. What is the recommended Databricks interface?

A) Deploy a custom Streamlit web app on Databricks Apps and send users the Databricks Apps URL, which they can open in a Teams tab via the Teams website hosting feature.
B) Use the Databricks Genie app for Microsoft Teams — admin installs it from the Microsoft marketplace, and business users interact with Genie Agents by mentioning `@Databricks Genie` directly in Teams channels.
C) Deploy a Databricks Model Serving endpoint and instruct the business users to send HTTP POST requests to the endpoint URL from the Teams chat box using the `/request` slash command.
D) Use Databricks Workflows to schedule a daily SQL report that is exported to a SharePoint folder, which Teams syncs as a channel notification — providing users with the latest data through their Teams interface.

**Correct Answer:** B
**Explanation:** B is correct. The Databricks Genie app for Microsoft Teams is the purpose-built integration for business users who live in Teams. A workspace admin installs the Genie app from the Microsoft App Marketplace (or through Microsoft Teams admin center), and users interact by mentioning `@Databricks Genie` in any Teams channel or chat. They can ask natural language questions about data, and the Genie Agent generates and executes the appropriate SQL queries, returning results directly in Teams. A is wrong because while Databricks Apps can be hosted as a web app, embedding a Streamlit app in Teams requires manual Teams Tab configuration and doesn't provide the seamless `@Genie` chat experience that business users expect. C is wrong because business users (non-technical) cannot be expected to craft HTTP POST requests from a chat interface — this is a developer-facing API pattern, not a business user interface. D is wrong because scheduled daily SQL reports are batch outputs, not interactive natural language querying — users cannot ask follow-up questions or explore data dynamically through a daily report export.
**Source:** Section 4: Assembling and Deploying – Objective 15: Develop an appropriate interactive user-facing interface — docs.databricks.com (search: "Databricks Genie app Slack Teams")

---

### Question 11
**Difficulty:** Intermediate

A developer stores an OpenAI API key required by their model serving endpoint. What is the Databricks-secure implementation?

A) Hardcode the OpenAI API key as a Python string constant in the model's `load_context()` method — since the source code is stored in a private Git repository with restricted access, the key is protected by Git repository access controls.
B) Store the key in a Databricks Secret Scope, reference it as an environment variable in the endpoint's serving configuration (e.g., `OPENAI_API_KEY`), and read it in `load_context()` via `os.environ["OPENAI_API_KEY"]`.
C) Store the key in a Unity Catalog Delta table row with column-level encryption enabled, and have the `predict()` method query this table on every request to retrieve the latest key value before each LLM call.
D) Pass the OpenAI API key as a parameter in the JSON inference request payload from the calling application, so each caller provides their own key and the endpoint never needs to store credentials internally.

**Correct Answer:** B
**Explanation:** B is correct. The Databricks-secure pattern for external API credentials is: (1) Store the key in a Databricks Secret Scope (an encrypted, access-controlled secret store). (2) Reference the secret as an environment variable in the Model Serving endpoint configuration — Databricks injects the secret's value as an environment variable at endpoint startup. (3) Read the environment variable in `load_context()` using `os.environ["OPENAI_API_KEY"]`. This pattern ensures the key is never in plain text in code or logs. A is wrong because hardcoding API keys in source code (even private repos) is a critical security anti-pattern — keys in source code can be leaked through git history, accidentally committed to public repos, or exposed in logs and error messages. C is wrong because querying a Delta table for the API key on every request adds latency to each inference call and is operationally complex — Databricks Secrets are the purpose-built secure credential store, not Delta tables. D is wrong because passing API keys in request payloads is a serious security exposure — they appear in network logs, Inference Table records, and could be intercepted in transit; each caller also needs to know the key.
**Source:** Section 4: Assembling and Deploying – Objective 2: Control access to resources from model serving endpoints — docs.databricks.com (search: "Databricks Secrets model serving")

---

### Question 12
**Difficulty:** Intermediate

A developer calls `mlflow.langchain.log_model()` without providing an `input_example`. They then try to register the model to Unity Catalog with `mlflow.register_model()`. What happens?

A) The registration succeeds normally — Unity Catalog model registration does not require a model signature; it only requires a valid MLflow run URI and a three-level namespace model name.
B) The registration fails with an error stating that a model signature is required for Unity Catalog registration — without an `input_example` to auto-infer the signature, the developer must manually define and attach a signature using `mlflow.models.infer_signature()`.
C) The registration succeeds but the serving endpoint created from this model will not accept any JSON payloads — it only accepts binary Parquet data because the missing signature defaults to a binary input schema.
D) The registration succeeds but MLflow assigns a default signature of `{inputs: string, outputs: string}` — the developer must update this in the Unity Catalog UI after registration before deploying to a serving endpoint.

**Correct Answer:** B
**Explanation:** B is correct. Unity Catalog requires a model signature for all registered models. The model signature defines the expected input/output schema (data types and column names) — Unity Catalog uses it to validate inference API payloads and to display the model's interface in Catalog Explorer. The easiest way to include a signature is to provide an `input_example` to `log_model()`, which causes MLflow to automatically infer the signature. Without either an `input_example` OR a manually defined signature, the `register_model()` call fails with a signature requirement error. A is wrong because Unity Catalog DOES require a model signature — this is a hard requirement for UC-registered models, unlike the legacy MLflow Model Registry which allowed signature-less models. C is wrong because there is no "defaults to binary Parquet" behavior — missing signatures cause a registration error, not a format downgrade. D is wrong because MLflow does not auto-assign a default `{string, string}` signature — missing signatures result in a registration failure, not a fallback schema.
**Source:** Section 4: Assembling and Deploying – Objective 5: Register the model to Unity Catalog using MLflow — docs.databricks.com (search: "Register model Unity Catalog MLflow" and "MLflow model signature input example")

---

### Question 13
**Difficulty:** Intermediate

A developer creates a Vector Search Delta Sync index using Databricks-managed embeddings. When a user submits a search query (`index.similarity_search(query_text="refund policy", num_results=5)`), what happens internally to the query text before the vector search is performed?

A) The query text is sent directly to the Vector Search index as a raw string — the index performs keyword matching (BM25) against the stored chunk text fields in the source Delta table, not against embedding vectors.
B) The query text is passed to the same embedding model endpoint specified during index creation (e.g., `databricks-bge-large-en`), which converts it to a vector — that query vector is then compared against the stored chunk embeddings using approximate nearest neighbor search.
C) The query text is first tokenized and chunked using the same chunking strategy applied to the source documents, then each query chunk is separately embedded and the results are aggregated across all query chunk matches.
D) The query text is sent to a Databricks-hosted cross-encoder model that scores it directly against all stored chunk texts in the Delta table, returning a ranked list without any embedding computation.

**Correct Answer:** B
**Explanation:** B is correct. When `similarity_search()` is called with `query_text`, the Vector Search service automatically sends the query text to the same embedding model endpoint that was specified in `embedding_model_endpoint_name` during index creation (e.g., `"databricks-bge-large-en"`). The embedding model converts the query text into a vector, and that query vector is compared against all stored chunk embeddings using an approximate nearest neighbor (ANN) algorithm (e.g., HNSW). The `num_results` most similar embeddings are returned. This guarantees that query and document embeddings are in the same vector space. A is wrong because Mosaic AI Vector Search is a semantic (dense vector) search system, not a keyword (BM25) search system — it compares embedding vectors, not raw text strings. C is wrong because user queries are not chunked before embedding — queries are typically short (a sentence or phrase) and are embedded as a single vector; query chunking would fragment the query's semantic meaning. D is wrong because cross-encoder reranking is an optional second-stage component added AFTER vector search returns candidates — it is not the primary search mechanism used by default in Vector Search.
**Source:** Section 4: Assembling and Deploying – Objective 6 & 8: Create/query Vector Search and key concepts — docs.databricks.com (search: "Query Vector Search index Databricks")

---

### Question 14
**Difficulty:** Intermediate

A company needs to run `ai_query()` for batch inference on 10 million rows. The data engineer attempts to run it on a Pro SQL Warehouse but gets an error. What is the correct compute requirement?

A) `ai_query()` requires a Classic SQL Warehouse with at least 4 worker nodes — Pro warehouses lack the distributed execution framework needed for batch AI inference workloads.
B) `ai_query()` requires a Serverless SQL Warehouse — it does not work on Pro or Classic warehouses because it relies on serverless compute's ability to dynamically scale and manage AI function execution.
C) `ai_query()` requires a Databricks cluster with Databricks Runtime ML 13.0+, not a SQL Warehouse — batch AI inference is a cluster-based operation, not a SQL warehouse operation.
D) `ai_query()` requires a Photon-enabled Pro Warehouse with at least 16 DBUs reserved — Photon acceleration is mandatory for AI function inference to achieve acceptable throughput on million-row datasets.

**Correct Answer:** B
**Explanation:** B is correct. `ai_query()` (and other SQL AI functions) specifically require a Serverless SQL Warehouse to execute. Pro and Classic SQL Warehouses do not support `ai_query()` — attempting to run it on these warehouse types results in an error. The Serverless SQL Warehouse provides the auto-scaling, managed infrastructure and the integrated AI function runtime needed for efficient batch inference. Databricks Runtime 18.2+ is also a requirement for some AI function features. A is wrong because Classic SQL Warehouses do not support `ai_query()` — the requirement is Serverless, not Classic. C is wrong because `ai_query()` is a SQL function designed for SQL Warehouses — not a cluster-based PySpark operation; cluster-based batch inference would use UDFs or `applyInPandas`. D is wrong because Photon is a vectorized query engine for analytical SQL — it does not enable `ai_query()` functionality, and Photon is not a requirement for AI functions.
**Source:** Section 4: Assembling and Deploying – Objective 9: Identify batch inference workloads and apply ai_query() — docs.databricks.com (search: "ai_query function Databricks SQL" and "Batch inference AI functions")

---

### Question 15
**Difficulty:** Intermediate

A developer builds a stateful customer service agent using LangGraph. The agent must remember the user's name and preferred language from previous sessions (cross-session memory), but also maintain the current conversation history within a single session (short-term memory). Which Databricks components handle each requirement?

A) Both short-term and long-term memory are handled by Databricks Inference Tables — the table captures all past inputs and outputs and the agent queries it at the start of each session to reconstruct the conversation context.
B) Short-term (within-session) memory is handled by LangGraph's Checkpointer (writing conversation turns to Lakebase using a thread ID), and long-term (cross-session) memory is handled by LangGraph's Store API reading/writing user preferences to Lakebase tables.
C) Both short-term and long-term memory are handled by Databricks Secrets — user names and preferences are stored as secret key-value pairs that the agent reads at the start of each session to reconstruct the user's context.
D) Short-term memory is handled by the LLM's internal attention mechanism (KV cache), and long-term memory is handled by Unity Catalog Delta tables that the agent explicitly queries using `ai_query()` at each session start.

**Correct Answer:** B
**Explanation:** B is correct. LangGraph provides two complementary memory mechanisms on Databricks: (1) **Short-term (within-session) memory** — LangGraph's Checkpointer persists the conversation state (all messages in the current thread) using a thread ID. The Checkpointer writes each new turn to a durable store (e.g., Lakebase Postgres table) so the agent can resume if interrupted. (2) **Long-term (cross-session) memory** — LangGraph's Store API provides a key-value persistence layer where the agent can write and read user-specific facts (name, language preference, past issues) across different sessions using a user ID as the namespace key. Lakebase (managed Postgres) is the recommended durable store for both. A is wrong because Inference Tables are a monitoring tool that logs production traffic for quality analysis — they are not designed or queried as a memory system for active agents. C is wrong because Databricks Secrets store machine credentials (API keys, passwords) — they are not a per-user preference store for agent memory. D is wrong because the LLM's KV cache is a performance optimization for token computation within a single call — it is ephemeral and not accessible as a persistent memory system.
**Source:** Section 4: Assembling and Deploying – Objective 11: Configure a persistent datastore to store and retrieve intermediate memory — docs.databricks.com (search: "Agent memory Databricks" and "Lakebase Databricks Postgres")

---

### Question 16
**Difficulty:** Intermediate

A team wants to use CI/CD for their RAG application with Databricks. They need to ensure the Vector Search index is always consistent with the source code. Which Databricks tool provides Infrastructure-as-Code for defining Vector Search indexes in a version-controlled configuration?

A) Databricks Delta Live Tables (DLT) — the team defines the Vector Search index as a DLT streaming table using the `@dlt.table()` decorator, and the DLT pipeline automatically creates and manages the index configuration.
B) Databricks Asset Bundles (DABs) — the team defines Vector Search endpoints, indexes, and Model Serving endpoints in a `databricks.yml` file that is checked into Git, and deploying the bundle creates or updates these resources consistently across environments.
C) Databricks Workflows — the team creates a Workflow that runs a deployment notebook on every Git push, and the notebook uses the Python SDK to create or update Vector Search indexes in the target environment.
D) MLflow Projects — the team defines the Vector Search index configuration as an MLflow Project entry point in `MLproject`, and `mlflow run` creates the index as part of the model training and deployment pipeline.

**Correct Answer:** B
**Explanation:** B is correct. Databricks Asset Bundles (DABs) is the Infrastructure-as-Code framework for Databricks. You define all infrastructure resources — Vector Search endpoints, Vector Search indexes, Model Serving endpoints, Workflows, and more — in a `databricks.yml` configuration file. This file is stored in Git alongside the application code. Running `databricks bundle deploy` creates or updates these resources in the target Databricks workspace, ensuring infrastructure is always consistent with the codebase. A is wrong because Delta Live Tables are for defining data transformation pipelines (ETL), not infrastructure resources like Vector Search indexes — there is no DLT concept of creating a Vector Search index via `@dlt.table()`. C is wrong because while a deployment notebook in a Workflow can create indexes programmatically, it is not IaC — the configuration is embedded in notebook code, not in a declarative configuration file that can be diffed and version-controlled as infrastructure. D is wrong because MLflow Projects define ML training workflows (parameters, entry points), not infrastructure provisioning — they cannot create Databricks-native resources like Vector Search indexes.
**Source:** Section 4: Assembling and Deploying – Objective 12: Apply CI/CD best practices — docs.databricks.com (search: "Databricks Asset Bundles CI/CD")

---

### Question 17
**Difficulty:** Intermediate

A developer builds a multi-agent system. The Supervisor agent needs to access GitHub repository data (issues, pull requests) via a standard MCP interface. Which type of MCP server should they use?

A) Managed MCP Server — Databricks provides a pre-built managed MCP server for GitHub that is available at zero configuration and requires no registration in Unity Catalog.
B) External MCP Server (MCP Service) — a third-party GitHub MCP server is registered as a Unity Catalog-governed "MCP Service" and connected via Unity AI Gateway, applying Databricks governance to external GitHub data access.
C) Custom MCP Server — the developer must build their own GitHub integration from scratch as a custom MCP server hosted on Databricks Apps, since no standard GitHub MCP server exists.
D) The Genie Agent MCP server — Genie Agents can query any external API including GitHub using natural language, so the Supervisor should connect to the Genie Agent's MCP URL instead of a GitHub-specific server.

**Correct Answer:** B
**Explanation:** B is correct. GitHub integration falls under the "External MCP Server" category — third-party services (GitHub, Slack, Jira, etc.) that have existing MCP server implementations. In Databricks, these are registered as Unity Catalog-governed "MCP Services" and all traffic routes through the Unity AI Gateway for centralized governance, auditability, and security policy enforcement. A is wrong because Databricks Managed MCP Servers only cover Databricks-native resources (Unity Catalog tables/functions, Vector Search indexes, Genie Agents) — GitHub is an external third-party service, not a Databricks-native resource. C is wrong because GitHub has existing open-source MCP server implementations (e.g., the official GitHub MCP server) — the developer does not need to build from scratch; they register the existing server as an External MCP Service. D is wrong because Genie Agents are specialized for natural language → SQL queries against Unity Catalog data tables — they are not general-purpose HTTP/API connectors and cannot query the GitHub API.
**Source:** Section 4: Assembling and Deploying – Objective 13: Integrate managed, external, and custom MCP servers — docs.databricks.com (search: "MCP servers Databricks" and "Unity Catalog MCP services")

---

### Question 18
**Difficulty:** Intermediate

A company's legal team reviews the MLflow Prompt Registry and asks: "If we change the production prompt and something goes wrong, can we see exactly what the prompt looked like before the change?" What does the Prompt Registry provide?

A) No — the MLflow Prompt Registry stores only the current active version of each prompt; previous versions are automatically deleted to conserve storage and keep the registry clean.
B) Yes — every change to a prompt creates an immutable, auto-numbered version snapshot with an optional commit message. The MLflow UI shows a diff between versions, and any previous version can be restored by re-assigning the `production` alias to it.
C) Yes — but only if the team manually exported the prompt template as a JSON file and saved it to a Unity Catalog Volume before making each change; the Prompt Registry itself does not maintain version history.
D) Yes — the Prompt Registry stores the last 5 versions of each prompt automatically. Versions older than 5 changes are permanently deleted, so teams must export older versions to external storage for long-term audit purposes.

**Correct Answer:** B
**Explanation:** B is correct. The MLflow Prompt Registry provides complete, immutable version history for all prompt changes. Key features: (1) Every registered prompt change creates a new auto-numbered version (1, 2, 3...) that is stored permanently and cannot be modified retroactively. (2) Each version can include a commit message documenting why the prompt was changed. (3) The MLflow UI shows diffs between versions. (4) Rolling back to any previous version is as simple as re-assigning the `production` alias to the older version number — no code changes required. A is wrong because the Prompt Registry is explicitly a version CONTROL system — it retains all historical versions, not just the current one; automatic deletion would defeat its entire audit purpose. C is wrong because the Prompt Registry maintains version history natively — no manual export to a Volume is needed; that would be a cumbersome workaround for a feature that is built-in. D is wrong because there is no 5-version limit in the MLflow Prompt Registry — all versions are retained indefinitely until explicitly deleted; the system does not auto-prune old versions.
**Source:** Section 4: Assembling and Deploying – Objective 14: Apply prompt version control and manage prompt lifecycle — docs.databricks.com (search: "MLflow Prompt Registry Databricks")

---

### Question 19
**Difficulty:** Intermediate

A developer wants to expose a custom agent as a web interface for internal users. The agent calls a Databricks Model Serving endpoint. The team has chosen Streamlit for the front-end framework. What is the correct Databricks deployment target for this Streamlit app?

A) Deploy the Streamlit app to Databricks Workflows as a long-running Task, using the Workflow's always-on execution mode to keep the web server running continuously for internal users.
B) Deploy the Streamlit app to Databricks Apps — Apps natively hosts Streamlit (and Gradio, Flask, FastAPI) web applications within the Databricks security perimeter, providing built-in SSO, Unity Catalog identity, and no separate infrastructure.
C) Deploy the Streamlit app to a Databricks job cluster using a Custom Docker Image containing the Streamlit server, with a port forwarding rule in the cluster configuration to expose the web interface.
D) Deploy the Streamlit app to Databricks Delta Live Tables as a continuous streaming pipeline, which runs the Streamlit server as a DLT processing node that handles user HTTP requests as streaming data events.

**Correct Answer:** B
**Explanation:** B is correct. Databricks Apps is the purpose-built service for hosting interactive web applications (Streamlit, Gradio, Flask, FastAPI) within the Databricks ecosystem. Key benefits: the app runs inside the Databricks security perimeter (SSO via Databricks identity), it can access Unity Catalog resources and call Model Serving endpoints using the user's identity, and there is no separate infrastructure to manage — Databricks handles the hosting. A is wrong because Databricks Workflows are for scheduled or triggered batch/streaming data and ML pipeline jobs — they do not support running persistent web servers that accept user HTTP requests. C is wrong because deploying a custom Docker image with port forwarding to a job cluster is a complex, unsupported workaround — job clusters are for computation tasks, not web application hosting; this approach is not supported by Databricks. D is wrong because Delta Live Tables is a declarative data pipeline framework (ETL) — it cannot host a Streamlit web server or handle HTTP requests from end users.
**Source:** Section 4: Assembling and Deploying – Objective 15: Develop an appropriate interactive user-facing interface — docs.databricks.com (search: "Databricks Apps deploy agent")

---

### Question 20
**Difficulty:** Intermediate

A developer needs to choose between a Delta Sync Index and a Direct Vector Access Index for their Vector Search setup. Their use case: they have a third-party system that computes specialized domain-specific embeddings (using a proprietary model not available as a Databricks endpoint) and they need to upload these pre-computed embeddings to the index. Which index type is correct?

A) Delta Sync Index with Databricks-managed embeddings — configure the index to use a Databricks Foundation Model API embedding endpoint and allow Databricks to recompute embeddings from the chunk text, overriding the third-party embeddings.
B) Direct Vector Access Index — this index type allows the developer to upload pre-computed embedding vectors directly, giving full control over the embedding computation without requiring a Databricks-hosted embedding model endpoint.
C) Delta Sync Index with self-managed embeddings — configure the source Delta table to include an embedding column pre-populated with the third-party embeddings, and the Delta Sync index reads the pre-computed values directly from that column.
D) Either index type works identically — both Delta Sync and Direct Vector Access indexes support pre-computed external embeddings through the same `embedding_vector` column specification in the source Delta table.

**Correct Answer:** C
**Explanation:** C is correct — and this is a nuanced choice. A Delta Sync Index with "self-managed embeddings" (where the source Delta table includes a pre-computed embedding column) allows the developer to use ANY embedding model, including proprietary third-party models. The developer computes embeddings externally, stores them as an array column in the Delta table, and the Delta Sync index reads and indexes these pre-computed vectors. This combines the convenience of Delta Sync (automatic CDF-based sync, no manual upload API calls) with the flexibility of external embedding computation. B is also a valid option (Direct Vector Access Index), but C is more appropriate because it leverages the Delta Sync automation (incremental updates via CDF) rather than requiring manual API calls to upload each batch of embeddings. A is wrong because the use case explicitly requires keeping the third-party embeddings — having Databricks recompute them with a different model defeats the purpose. D is wrong because the two index types have fundamentally different APIs and behaviors — they are not identical.
**Source:** Section 4: Assembling and Deploying – Objective 8 & 10: Key concepts of Vector Search and configuration — docs.databricks.com (search: "Mosaic AI Vector Search overview" and "Mosaic AI Vector Search configuration")
