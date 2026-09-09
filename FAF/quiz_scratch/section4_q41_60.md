### Question 41
**Difficulty:** Beginner

A developer has a source Delta table `main.docs.chunks` and wants to create a Vector Search index that automatically stays up-to-date as new chunks are appended. What prerequisite must be enabled on the Delta table before creating a Delta Sync index?

A) The Delta table must have `delta.enableAutoOptimize = true` set as a table property — Auto Optimize compacts small files, which is required for Vector Search's incremental change detection.
B) The Delta table must have Change Data Feed (CDF) enabled: `ALTER TABLE main.docs.chunks SET TBLPROPERTIES (delta.enableChangeDataFeed = true)` — CDF produces a changelog of inserts, updates, and deletes that the Delta Sync pipeline reads to keep the index current.
C) The Delta table must be converted to a Unity Catalog Managed Table with `CONVERT TO MANAGED TABLE main.docs.chunks` — Vector Search Delta Sync indexes only work with Unity Catalog managed tables, not external tables.
D) The Delta table must have row-level security disabled on the `chunk_text` column using `ALTER TABLE main.docs.chunks DROP ROW FILTER` — row filters block the Vector Search service from reading the full table content for indexing.

**Correct Answer:** B
**Explanation:** B is correct. Change Data Feed (CDF) is a mandatory prerequisite for creating a Delta Sync Vector Search index. CDF records every data change (INSERT, UPDATE, DELETE) in a special `_change_data` directory alongside the Delta table's main data files. The Vector Search Delta Sync pipeline reads this CDF to identify which chunks are new, updated, or deleted, and processes only those changes — making incremental sync efficient for large tables. Without CDF enabled, the Vector Search service has no way to detect changes and the index creation fails. A is wrong because `enableAutoOptimize` compacts small files for query performance, but it is not required for Vector Search — CDF is the mandatory prerequisite. C is wrong because Delta Sync indexes work with both UC Managed and UC External tables — the requirement is CDF enablement, not table type conversion. D is wrong because row-level security is applied at query time (to restrict what data users can retrieve), not at index build time — it does not block the Vector Search service from indexing content for users authorized to access it.
**Source:** Section 4: Assembling and Deploying – Objective 6: Create and query a Vector Search index — docs.databricks.com (search: "Create Mosaic AI Vector Search index")

---

### Question 42
**Difficulty:** Beginner

A developer writes `mlflow.set_registry_uri("databricks-uc")` at the start of their MLflow logging script. What does this line accomplish?

A) It sets the MLflow tracking server's backend store to Unity Catalog, routing all experiment runs, metrics, and artifacts to the Unity Catalog-managed MLflow tracking server rather than the workspace-local tracking server.
B) It tells MLflow to register all subsequently logged models to the Unity Catalog Model Registry (using the three-level namespace) instead of the legacy workspace-level MLflow Model Registry — enabling Unity Catalog governance, versioning, and permissions on registered models.
C) It enables Unity Catalog authentication for the current MLflow session, requiring all model logging operations to use the caller's Unity Catalog identity and pass through Unity Catalog access control checks.
D) It migrates all existing models in the legacy MLflow Model Registry to Unity Catalog, performing a one-time bulk migration of model versions and their associated metadata to the Unity Catalog registry.

**Correct Answer:** B
**Explanation:** B is correct. `mlflow.set_registry_uri("databricks-uc")` switches the target model registry from the legacy workspace-level MLflow Model Registry to the Unity Catalog Model Registry. After this call, any `mlflow.register_model()` call or `registered_model_name` parameter in `log_model()` will register the model as a Unity Catalog three-level namespace object (e.g., `catalog.schema.model_name`). The model then inherits Unity Catalog governance: RBAC permissions, cross-workspace discovery, lineage tracking, and model version management. A is wrong because `set_registry_uri` changes the MODEL REGISTRY destination, not the experiment/tracking server — the tracking server stores runs, metrics, and artifacts separately from the model registry. C is wrong because Unity Catalog authentication for the current session is established at workspace login, not by `set_registry_uri` — this call only affects where models are registered. D is wrong because `set_registry_uri` is not a migration command — it does not touch existing model registry entries; it only affects where FUTURE `register_model()` calls go.
**Source:** Section 4: Assembling and Deploying – Objective 5: Register the model to Unity Catalog using MLflow — docs.databricks.com (search: "Register model Unity Catalog MLflow")

---

### Question 43
**Difficulty:** Beginner

A developer asks: "What is the difference between a Vector Search Endpoint and a Vector Search Index?" Select the correct explanation.

A) A Vector Search Endpoint is the query interface (the REST API URL) that client applications call to run similarity searches; a Vector Search Index is a physical storage object (similar to a database table) that the Endpoint queries internally.
B) A Vector Search Endpoint is the compute cluster managed by Databricks that serves one or more indexes; a Vector Search Index is the actual data structure containing the embedded vectors, stored as a Unity Catalog object and served by the endpoint.
C) A Vector Search Endpoint is a Databricks Model Serving endpoint configured to use the `embeddings` task type; a Vector Search Index is a Delta table with an added vector column, which the endpoint queries using Spark DataFrame operations.
D) A Vector Search Endpoint and a Vector Search Index are interchangeable terms — both refer to the same resource that stores embeddings and exposes a similarity search API; the different names reflect different API versions.

**Correct Answer:** B
**Explanation:** B is correct. These are two distinct resources with a parent-child relationship: (1) **Vector Search Endpoint** — a compute cluster managed by Databricks that provides the serving infrastructure. It must be created FIRST before any indexes can be created. One endpoint can serve multiple indexes. It is analogous to a database server. (2) **Vector Search Index** — the actual Unity Catalog object that stores the embedded vectors (as an ANN index structure), linked to a source Delta table via CDF, and served by the parent endpoint. It is analogous to a database table. The typical setup: one Vector Search Endpoint hosts multiple Vector Search Indexes for different knowledge bases. A is wrong because the Endpoint is not just a "REST API URL" — it is a compute cluster that runs the ANN search algorithm. The index is not just queried through the endpoint; the endpoint IS the compute that runs the search. C is wrong because Vector Search Endpoints are completely separate from Databricks Model Serving endpoints — they are a different service; and Vector Search Indexes are NOT Delta tables with vector columns, they are specialized ANN index data structures. D is wrong because Endpoint and Index are distinct resources with different APIs, different creation parameters, and different management lifecycles.
**Source:** Section 4: Assembling and Deploying – Objective 8: Explain key concepts and components of Mosaic AI Vector Search — docs.databricks.com (search: "Mosaic AI Vector Search overview")

---

### Question 44
**Difficulty:** Beginner

A developer wants to test their pyfunc model locally before deploying to a Model Serving endpoint. After logging the model with `mlflow.pyfunc.log_model()`, they load it with `mlflow.pyfunc.load_model(model_uri)`. What object does `load_model()` return, and how do they call it?

A) It returns an instance of the developer's `CustomRAGChain` class directly — they can call any method defined on the class, including private helper methods like `_preprocess()` and `_postprocess()`.
B) It returns an `mlflow.pyfunc.PyFuncModel` wrapper object — they call its `predict(data)` method, passing a Pandas DataFrame matching the model's input schema, which internally calls their `CustomRAGChain.predict()`.
C) It returns a Python dictionary containing the model's configuration (endpoint URL, signature, dependencies) — they must instantiate the model class manually using `CustomRAGChain(**model_dict)` before calling `predict()`.
D) It returns a Flask web server object running on localhost port 5000 — they test the model by sending HTTP POST requests to `http://localhost:5000/invocations` using the `requests` library.

**Correct Answer:** B
**Explanation:** B is correct. `mlflow.pyfunc.load_model()` returns an `mlflow.pyfunc.PyFuncModel` object — a standardized MLflow wrapper that encapsulates the underlying model (whether it's a `PythonModel`, LangChain chain, or sklearn estimator). This wrapper exposes a uniform `predict(data)` method that accepts a Pandas DataFrame matching the model's input signature. Internally, `PyFuncModel.predict()` calls the developer's `CustomRAGChain.predict()` with the appropriate context. This allows local testing with the same interface that the Model Serving endpoint uses. A is wrong because `load_model()` does NOT return the raw `CustomRAGChain` instance — it returns the `PyFuncModel` wrapper; private methods like `_preprocess()` are not directly accessible on the returned object. C is wrong because `load_model()` returns a ready-to-use model object, not a configuration dictionary; the model is fully instantiated (including `load_context()` having been called). D is wrong because `load_model()` does not start a web server — `mlflow models serve` (a separate CLI command) starts the Flask server for local REST endpoint testing; `load_model()` is for in-process Python testing.
**Source:** Section 4: Assembling and Deploying – Objective 1: Code a chain using a pyfunc model — docs.databricks.com (search: "Deploy custom Python model Databricks Model Serving")

---

### Question 45
**Difficulty:** Beginner

A customer support team wants their employees to interact with a Databricks-hosted chatbot directly from Slack. The chatbot answers questions using a Databricks RAG pipeline. What setup does this require?

A) The Slack administrator installs a custom Slack app that makes HTTP POST requests to the Databricks Model Serving REST endpoint on each user message, using a Service Principal's token stored in Slack's secret manager.
B) The Databricks workspace administrator enables the Databricks Genie app for Slack — admins configure which Genie Agents to expose to Slack, and users interact by mentioning `@Genie` in Slack channels or direct messages.
C) Employees must download the Databricks mobile app and connect it to Slack via the Zapier integration, which bridges Slack messages to Databricks notebook API calls and returns the chatbot's response as a Slack message.
D) The development team deploys a Streamlit app on Databricks Apps with a Slack webhook integration — when users send a Slack message, the webhook triggers the Streamlit app's backend, which calls the chatbot and posts the response to Slack.

**Correct Answer:** B
**Explanation:** B is correct. The Databricks Genie app for Slack is the purpose-built integration for exposing Databricks conversational agents in Slack. A workspace admin enables the Genie app (available as a Slack app from Databricks), configures which Genie Agents (knowledge bases) are accessible, and pins specific agents to channels. Employees then interact by mentioning `@Genie` (or `@Databricks Genie`) in any Slack channel or DM — asking questions in natural language and receiving answers directly in Slack. A is wrong because while a custom Slack app calling the Model Serving REST endpoint is technically possible, it requires significant custom engineering (Slack app development, webhook handling, token management) — the Databricks Genie Slack app is the purpose-built zero-custom-code solution. C is wrong because there is no "Databricks mobile app to Slack via Zapier" integration — this is not a real Databricks product integration. D is wrong because building a Streamlit-Slack webhook bridge is a complex custom integration that requires maintaining a webhook server — the Genie Slack app provides this out-of-the-box.
**Source:** Section 4: Assembling and Deploying – Objective 15: Develop an appropriate interactive user-facing interface — docs.databricks.com (search: "Databricks Genie app Slack Teams")

---

### Question 46
**Difficulty:** Intermediate

A developer's RAG chain requires the `langchain`, `databricks-vectorsearch`, and `openai` Python packages at serving time. How should these dependencies be specified when logging the model?

A) Include them in a `requirements.txt` file in the same directory as the notebook — the Databricks Model Serving runtime automatically reads `requirements.txt` from the workspace's root directory when deploying any new model version.
B) Pass them as a list to the `pip_requirements` parameter of `mlflow.langchain.log_model()` or `mlflow.pyfunc.log_model()` — MLflow bundles this list with the model artifact, and the serving environment installs these packages when the endpoint starts.
C) Install the packages with `%pip install langchain databricks-vectorsearch openai` in the first cell of the deployment notebook — the serving runtime automatically captures all packages installed in the notebook environment and replicates them.
D) Add the packages to the Databricks cluster configuration's "Advanced Options → Init Script" field — the serving endpoint uses the same cluster configuration as the development cluster, inheriting all installed packages.

**Correct Answer:** B
**Explanation:** B is correct. Dependencies for MLflow models are specified via the `pip_requirements` parameter (or `conda_env` for Conda environments) in `mlflow.*log_model()` calls. These are stored as part of the model artifact (in `requirements.txt` within the MLflow model directory). When a Model Serving endpoint starts, the serving runtime reads these requirements and installs the specified packages in an isolated environment before loading the model. This ensures reproducibility — the serving environment exactly matches the dependencies declared at log time. A is wrong because there is no automatic `requirements.txt` discovery from the workspace root — Model Serving environments are isolated containers that only install what is declared in the model's `pip_requirements` artifact. C is wrong because `%pip install` in a development notebook installs packages in the interactive cluster's environment — this is NOT automatically captured or replicated to the Model Serving environment; serving environments are independent isolated containers. D is wrong because Model Serving endpoints do NOT use the development cluster's configuration — they run on dedicated managed compute with isolated environments defined by the model's logged dependencies.
**Source:** Section 4: Assembling and Deploying – Objective 4: Choose basic elements needed to create a RAG application — docs.databricks.com (search: "Build a RAG chatbot Mosaic AI")

---

### Question 47
**Difficulty:** Intermediate

A developer adds custom pre-processing to their pyfunc `predict()` method:

```python
def predict(self, context, model_input):
    query = model_input["query"].iloc[0]
    if len(query) > 2000:
        query = query[:2000]  # truncate long inputs
    response = self.llm.invoke(query)
    return pd.DataFrame({"answer": [response.content]})
```

What potential issue exists with returning `pd.DataFrame({"answer": [response.content]})` instead of a simple string?

A) Returning a Pandas DataFrame from `predict()` is invalid — `mlflow.pyfunc.PythonModel.predict()` must always return a Python dictionary, and returning a DataFrame causes a serialization error in the serving runtime.
B) Returning a single-column DataFrame is valid and the standard pyfunc return format. However, the calling REST API client receives a JSON response with the DataFrame serialized as `{"predictions": [{"answer": "..."}]}` — clients must parse this nested structure to extract the answer string.
C) Returning a Pandas DataFrame causes a performance issue in the serving runtime — DataFrames are serialized to Apache Arrow format before transmission, adding 50–200ms of overhead per request compared to returning a raw string.
D) Returning a Pandas DataFrame works locally but fails in Model Serving because the serving runtime uses Spark to process inference results, and Pandas DataFrames are not compatible with the Spark serialization layer used by Model Serving endpoints.

**Correct Answer:** B
**Explanation:** B is correct. `mlflow.pyfunc.PythonModel.predict()` can return Pandas DataFrames, and this is a common and valid return format. The serving runtime serializes the DataFrame to JSON in the MLflow inference response format: `{"predictions": [{"answer": "the actual answer text"}]}`. API clients must parse this nested JSON structure to extract the answer. This is important for client developers to know — if they expect a plain string response, they need to handle the nested `predictions[0]["answer"]` path. A is wrong because Pandas DataFrames are a fully supported return type for `predict()` — along with numpy arrays, Python lists, and dictionaries. The standard pyfunc interface explicitly supports multiple return types. C is wrong because while Apache Arrow serialization is used internally, the overhead is measured in milliseconds at most and is not typically a practical concern for most RAG applications where LLM call latency dominates (usually 200ms–2s). D is wrong because Databricks Model Serving runs Python serving code in an isolated Python process, not inside Spark — it does not use Spark serialization for inference responses; Pandas DataFrames work correctly in the serving environment.
**Source:** Section 4: Assembling and Deploying – Objective 1: Code a chain using a pyfunc model — docs.databricks.com (search: "mlflow.pyfunc PythonModel custom")

---

### Question 48
**Difficulty:** Intermediate

A company deploys a RAG application using a Databricks Model Serving endpoint. The security team asks: "When the endpoint calls our internal Vector Search index, whose Unity Catalog credentials are used?" What is the correct answer?

A) The endpoint always uses the `databricks-service-principal@system` anonymous system account for all Unity Catalog data access — individual user identities are not propagated to the serving endpoint's internal resource calls.
B) The endpoint uses the Unity Catalog identity of the user who CREATED the endpoint — this identity is permanently bound to the endpoint at creation time and determines which Unity Catalog resources (Vector Search indexes, Delta tables, UC Functions) the endpoint can access.
C) The endpoint uses the identity of the USER making the inference API call — each incoming request propagates the caller's identity to all downstream Unity Catalog resource access within the serving endpoint.
D) The endpoint uses a rotating service account identity automatically provisioned by Databricks Model Serving — this identity has read-only access to all resources in the workspace and is refreshed every 24 hours for security.

**Correct Answer:** B
**Explanation:** B is correct. This is a critical security concept for Model Serving. The endpoint's Unity Catalog data access identity is permanently bound to the identity of the user (or Service Principal) who CREATED the serving endpoint — not the user making individual inference requests. This "creator identity" is used for all internal resource access: querying Vector Search indexes, reading Delta tables, executing Unity Catalog Functions, accessing Volume files. This is why best practice requires creating production endpoints under a dedicated Service Principal (not a personal user account) — the endpoint's data access capabilities are determined by that Service Principal's Unity Catalog permissions. A is wrong because there is no `databricks-service-principal@system` anonymous account — endpoint access is tied to a specific real identity (the creator). C is wrong because caller identity propagation for data access does NOT occur in Databricks Model Serving — the endpoint uses the creator's identity for internal resource calls, regardless of who is calling the inference API. D is wrong because Databricks does not automatically provision rotating service accounts for Model Serving endpoints — the creator's identity is static (not rotating) and is set permanently at endpoint creation.
**Source:** Section 4: Assembling and Deploying – Objective 2: Control access to resources from model serving endpoints — docs.databricks.com (search: "Model serving endpoint permissions Databricks")

---

### Question 49
**Difficulty:** Intermediate

A developer creates a Vector Search index with `pipeline_type="CONTINUOUS"`. The source Delta table receives updates every 30 seconds from a streaming job. A product manager asks: "How long after a new document is added to the source table will it be searchable?" What is the correct answer?

A) New documents are searchable immediately (0ms latency) — CONTINUOUS sync hooks into Delta Lake's commit log at the transaction level, making vectors available to search before the transaction is even visible to other readers.
B) New documents typically become searchable within seconds to a few minutes — CONTINUOUS sync monitors the Change Data Feed and processes new entries rapidly, but there is inherent pipeline latency for reading CDF, computing embeddings, and updating the ANN index.
C) New documents become searchable within exactly 5 minutes — Databricks guarantees a maximum of 5 minutes sync latency for CONTINUOUS pipeline type, with SLA enforcement via automatic escalation to on-call infrastructure teams.
D) New documents become searchable on the next scheduled sync window — even with CONTINUOUS mode enabled, Databricks batches changes into 15-minute windows to optimize embedding computation costs and ANN index update efficiency.

**Correct Answer:** B
**Explanation:** B is correct. CONTINUOUS sync is near real-time but not zero-latency. The pipeline: (1) The CDF log records the new Delta table transaction. (2) The CONTINUOUS sync pipeline detects the CDF entry (typically within seconds). (3) The new chunk text is sent to the embedding model endpoint for vectorization (adds latency proportional to text length and model throughput). (4) The new vector is added to the ANN index. (5) The vector becomes searchable. Total latency is typically seconds to a few minutes, depending on the embedding model's response time and current processing queue depth. This is called "near real-time" rather than "real-time" because of these inherent pipeline stages. A is wrong because no embedding system can make vectors searchable before the embedding computation is complete — zero-latency would require vectors to be pre-computed before document insertion. C is wrong because there is no Databricks contractual guarantee of exactly 5 minutes for CONTINUOUS sync — it is typically much faster; and "on-call escalation" is not a feature of sync latency SLAs. D is wrong because CONTINUOUS sync does NOT batch into 15-minute windows — that would make it indistinguishable from TRIGGERED sync; the defining characteristic of CONTINUOUS is ongoing, event-driven processing.
**Source:** Section 4: Assembling and Deploying – Objective 10: Configure vector search based on requirements — docs.databricks.com (search: "Mosaic AI Vector Search configuration")

---

### Question 50
**Difficulty:** Intermediate

A developer uses the MLflow Prompt Registry and loads a prompt with `mlflow.load_prompt("prompts:/rag_system_prompt/production")`. What Python object is returned, and how is it used to assemble a LangChain prompt?

A) It returns a Python string containing the full prompt template text — the string can be directly passed to `ChatPromptTemplate.from_messages([("system", prompt_text)])` to create a LangChain chat prompt.
B) It returns an `mlflow.models.Prompt` object with a `.template` attribute (the prompt text string) and a `.version` attribute (the version number). To use in LangChain: extract `prompt.template` and pass it to `ChatPromptTemplate.from_messages([("system", prompt.template)])`.
C) It returns a LangChain `ChatPromptTemplate` object directly — the MLflow Prompt Registry stores prompts pre-formatted as LangChain objects, enabling direct use in LCEL chains without any conversion step.
D) It returns a callable `PromptFunction` object — calling it with keyword arguments (`prompt_func(context=..., question=...)`) returns the assembled prompt string with variables substituted, without needing to import or use LangChain.

**Correct Answer:** B
**Explanation:** B is correct. `mlflow.load_prompt()` returns an `mlflow.models.Prompt` object (or `mlflow.prompt.Prompt`). This object contains: (1) `.template` — the raw prompt text string (with placeholder variables like `{context}` and `{question}`). (2) `.version` — the version number of the loaded prompt. (3) `.name` — the registered prompt name. To use in LangChain, the developer extracts the template string and passes it to the appropriate LangChain constructor: `ChatPromptTemplate.from_messages([("system", prompt.template), ("human", "{question}")])`. A is wrong because `mlflow.load_prompt()` does NOT return a raw string — it returns an `mlflow.models.Prompt` object; accessing the string requires `.template`. C is wrong because the Prompt Registry stores template strings, not framework-specific objects — it is framework-agnostic and stores raw text that developers integrate into any framework (LangChain, LlamaIndex, custom code). D is wrong because there is no `PromptFunction` callable type in the MLflow Prompt Registry — the returned object is a `Prompt` data class with attributes, not a callable function that performs variable substitution.
**Source:** Section 4: Assembling and Deploying – Objective 14: Apply prompt version control and manage prompt lifecycle — docs.databricks.com (search: "MLflow Prompt Registry Databricks")

---

### Question 51
**Difficulty:** Advanced

A developer runs `mlflow.pyfunc.log_model()` but forgets to include `databricks-vectorsearch` in `pip_requirements`. The model works during local testing (because the library is installed in the development cluster) but fails in production. What error occurs, and how should it be fixed without re-running the training pipeline?

A) The model fails with `ImportError: No module named 'databricks.vector_search'` when the serving endpoint tries to load the model's dependencies. Fix: use `mlflow.models.add_pip_requirements(model_uri, ["databricks-vectorsearch"])` to append the missing package without re-logging.
B) The model fails with a `ModelSignatureError` because `databricks-vectorsearch` is part of the model signature definition and its absence causes schema validation to fail. Fix: re-log the model with `pip_requirements` corrected and `input_example` included.
C) The model fails silently — the Vector Search calls are skipped if `databricks-vectorsearch` is not installed, and the serving endpoint falls back to keyword-based search using the source Delta table directly, degrading retrieval quality.
D) The model fails with a `DatabricksVersionError: vectorsearch requires Databricks Runtime 15.0+` because the serving runtime defaults to an older runtime version. Fix: set the endpoint's runtime version to 15.0+ in the endpoint configuration YAML.

**Correct Answer:** A
**Explanation:** A is correct. When a Python package listed in `load_context()` or `predict()` is imported but missing from `pip_requirements`, the Model Serving endpoint fails with `ImportError` when the serving container tries to load the model. The fix WITHOUT re-running the full training pipeline: use `mlflow.models.add_pip_requirements(model_uri="runs:/<run_id>/model", requirements=["databricks-vectorsearch==0.x.y"])` to append the missing package to the already-logged model artifact's `requirements.txt`. This modifies only the dependency specification without touching the model weights, code, or signature. Alternatively, use `mlflow.pyfunc.get_model_dependencies(model_uri)` to inspect what was originally logged. B is wrong because `databricks-vectorsearch` is a Python runtime library, not a model signature component — its absence causes an `ImportError`, not a `ModelSignatureError`. C is wrong because Python does not "silently skip" missing imports — attempting to import a missing module raises `ImportError` immediately; there is no fallback to keyword search. D is wrong because `databricks-vectorsearch` library compatibility is unrelated to Databricks Runtime version in this context — the error is a missing package, not a runtime version incompatibility.
**Source:** Section 4: Assembling and Deploying – Objective 4: Choose basic elements needed to create a RAG application — docs.databricks.com (search: "Build a RAG chatbot Mosaic AI" and "mlflow.pyfunc PythonModel custom")

---

### Question 52
**Difficulty:** Advanced

A team implements a CI/CD pipeline with three environments: dev, staging, production. The MLflow Prompt Registry has a prompt `main.ml.support_prompt` with: version 1 (alias: `dev`), version 2 (alias: `staging`), version 3 (alias: `production`). The application loads with `mlflow.load_prompt("prompts:/main.ml.support_prompt/production")`. After a successful staging evaluation, the team wants to promote version 2 to production without any code changes. What is the exact sequence of actions?

A) (1) Delete the `production` alias from version 3 → (2) Assign the `production` alias to version 2 → (3) Application automatically loads version 2 on the next inference request without endpoint redeployment.
B) (1) Register a new version 4 that is a copy of version 2 → (2) Assign `production` alias to version 4 → (3) Redeploy the Model Serving endpoint to pick up the new prompt version → (4) Application loads version 4 (the copy of the staging prompt).
C) (1) Re-assign the `production` alias to point to version 2 in the MLflow Prompt Registry UI or via `mlflow.client.MlflowClient().set_registered_model_alias(name="main.ml.support_prompt", alias="production", version=2)` → (2) The application loads version 2 on the next call without any code or endpoint changes.
D) (1) Export version 2's prompt text to a text file → (2) Import it as a new version in the `production` catalog schema → (3) Update the application code to load from the new version URI → (4) Redeploy the serving endpoint.

**Correct Answer:** C
**Explanation:** C is correct. The alias-based promotion workflow is the core value of MLflow Prompt Registry: (1) The team re-assigns the `production` alias to version 2 (previously on version 3). This can be done via the MLflow UI or `MlflowClient().set_registered_model_alias(name="main.ml.support_prompt", alias="production", version=2)`. (2) The application code `mlflow.load_prompt("prompts:/main.ml.support_prompt/production")` always resolves the `production` alias at LOAD TIME — on the next inference request, it fetches the current target of the `production` alias, which is now version 2. (3) No code changes, no model re-logging, no endpoint redeployment needed — the prompt update is zero-downtime and instant. A is wrong because deleting the `production` alias from version 3 before assigning it to version 2 would create a brief window where `production` alias is unassigned — the application would throw a `PromptVersionNotFound` error. The correct order is to assign first (MLflow reassigns atomically). B is wrong because creating a copy as version 4 is unnecessary overhead — and requiring an endpoint redeployment defeats the purpose of alias-based promotion (which specifically avoids redeployment). D is wrong because alias-based promotion was invented precisely to eliminate this export/reimport/redeploy workflow.
**Source:** Section 4: Assembling and Deploying – Objective 14: Apply prompt version control and manage prompt lifecycle — docs.databricks.com (search: "MLflow Prompt Registry Databricks" and "MLflow Prompt Registry aliases")

---

### Question 53
**Difficulty:** Advanced

A team develops a multi-step RAG agent where the `predict()` method of their pyfunc model calls Vector Search, then an LLM, then applies post-processing. They want to test only the post-processing step in isolation. Which testing approach is most correct?

A) Deploy the full model to a staging endpoint and send carefully crafted test inputs that bypass the Vector Search and LLM steps by including `skip_retrieval=true` in the request payload — a flag the `predict()` method checks to short-circuit earlier steps.
B) Extract the `_postprocess()` method (or equivalent logic) from the pyfunc class and test it independently as a pure Python function using `pytest` — unit testing post-processing logic requires only Python inputs and assertions, not any MLflow or Databricks infrastructure.
C) Use `mlflow.pyfunc.load_model()` to load the full model and call `predict()` with inputs that are pre-formatted to skip pre-processing — MLflow's pyfunc interface automatically detects formatted inputs and routes them directly to `_postprocess()`.
D) Create a separate MLflow run with a pyfunc model that contains only the `_postprocess()` method, log it independently, deploy to a separate serving endpoint, and test through that endpoint — modular endpoint testing is the standard approach for component isolation.

**Correct Answer:** B
**Explanation:** B is correct. Post-processing logic in a pyfunc model (like JSON parsing, confidence filtering, citation formatting) is pure Python business logic that takes some input and returns a transformed output. The correct, efficient testing approach is to extract and test this logic as an independent Python function: `from my_module import postprocess_response; result = postprocess_response(sample_llm_output); assert result["confidence"] > 0.7`. This runs in milliseconds without any infrastructure, making it fast and suitable for CI. A is wrong because adding `skip_retrieval=true` request-level flags is an anti-pattern — the production code should not include test-bypass logic; it adds maintenance overhead and can mask real integration issues. C is wrong because MLflow pyfunc `predict()` does not have built-in routing based on input formatting — it calls the full `predict()` method as implemented; MLflow provides no "automatic step skipping" feature. D is wrong because deploying a separate endpoint just to test a post-processing function is vastly over-engineered — post-processing is pure Python and needs no serving infrastructure for unit testing.
**Source:** Section 4: Assembling and Deploying – Objective 12: Apply CI/CD best practices — docs.databricks.com (search: "Databricks Asset Bundles CI/CD")

---

### Question 54
**Difficulty:** Advanced

A developer creates a RAG chain where the input is a list of user messages in OpenAI chat format:
```json
{"messages": [{"role": "user", "content": "What is the return policy?"}]}
```
They want to log this with the correct MLflow signature. Which code correctly defines the signature?

A)
```python
from mlflow.models import infer_signature
import pandas as pd
input_example = pd.DataFrame([{"messages": '[{"role": "user", "content": "test"}]'}])
signature = infer_signature(input_example, pd.DataFrame([{"response": "test answer"}]))
```

B)
```python
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import Schema, ColSpec
signature = ModelSignature(
    inputs=Schema([ColSpec("string", "messages")]),
    outputs=Schema([ColSpec("string", "response")])
)
```

C)
```python
from mlflow.models import infer_signature
input_example = {"messages": [{"role": "user", "content": "What is the return policy?"}]}
output_example = {"response": "Our return policy is 30 days."}
signature = infer_signature(model_input=input_example, model_output=output_example)
```

D)
```python
import mlflow
mlflow.langchain.log_model(
    lc_model=chain,
    artifact_path="chain",
    input_example={"messages": [{"role": "user", "content": "What is the return policy?"}]}
)
# MLflow auto-infers the correct complex schema from the input_example
```

**Correct Answer:** D
**Explanation:** D is correct and is the recommended approach for LangChain models. When `input_example` is provided to `mlflow.langchain.log_model()`, MLflow 2.5+ automatically inspects the example, infers the complete schema (including nested list-of-dicts structures like the OpenAI messages format), and creates the model signature automatically. This handles complex nested schemas (lists, dicts, lists of dicts) that manual signature definition is error-prone for. The developer doesn't need to manually construct the signature. A is partially correct (provides an input_example to `infer_signature`) but incorrectly serializes the messages list as a JSON string in a DataFrame column — this changes the schema from nested objects to a flat string, which doesn't match the actual input format. B is wrong because `ColSpec("string", "messages")` defines `messages` as a single string column, not as a list of message objects — this schema mismatch would cause payload validation failures for structured chat inputs. C is wrong because `infer_signature()` with raw dictionaries (not DataFrames) may not correctly infer the schema for list-of-dict inputs — `infer_signature` requires Pandas DataFrames or numpy arrays for reliable schema inference. D is correct and also the simplest approach.
**Source:** Section 4: Assembling and Deploying – Objective 4 & 5: RAG elements and Unity Catalog registration — docs.databricks.com (search: "MLflow model signature input example" and "Register model Unity Catalog MLflow")

---

### Question 55
**Difficulty:** Advanced

A data engineer is implementing a batch inference pipeline using `ai_query()` to extract structured JSON from 1 million contract documents. After the pipeline runs, the Query Profile shows 150,000 rows have `null` in the `extracted_json` column. What should they investigate, and what remediation applies?

A) The 150,000 nulls indicate that the Model Serving endpoint rate limit was hit for those rows — they should rerun with a smaller batch size (e.g., process 850,000 rows first, then 150,000 in a second run) to stay within rate limits.
B) The 150,000 nulls typically indicate either: (a) the LLM failed to extract valid JSON for those contracts (model error — investigate contract characteristics for those rows), (b) those contracts exceeded the context window limit (investigate average text length for null rows), or (c) timeout errors for very long contracts. Remediation: filter for null rows, investigate patterns (text length, contract type), and apply targeted pre-processing (truncation, summarization) before re-running inference on the failed rows.
C) The 150,000 nulls are expected — `ai_query()` returns null for all rows where the model returns an answer with confidence below 0.7, and the developer should tune the confidence threshold parameter to reduce null outputs.
D) The 150,000 nulls indicate that the Serverless SQL Warehouse ran out of memory — rerun the query on a Classic SQL Warehouse with at least 32GB of driver memory to handle the full 1 million row batch without OOM errors.

**Correct Answer:** B
**Explanation:** B is correct. `ai_query()` returns `null` when the model call fails for a specific row, which can happen due to multiple causes: (1) **Model error** — the LLM could not produce valid JSON for that contract's content (malformed prompts, unusual content structure). (2) **Context window exceeded** — contracts longer than the model's context window cause the inference call to fail. (3) **Timeout** — very long contracts take too long to process and the request times out. The correct investigation approach: `SELECT id, LENGTH(contract_text), extracted_json IS NULL AS failed FROM results WHERE extracted_json IS NULL` — check if null rows correlate with long text (context window issue) or certain contract types (model failure pattern). A is wrong because rate limit failures in `ai_query()` are handled internally with automatic retries — they would appear as delays or partial null patterns, not as a consistent 15% failure rate; and rerunning a "smaller batch" doesn't fix rate limits. C is wrong because `ai_query()` has no built-in "confidence threshold" parameter — null results indicate inference failures, not low-confidence outputs. D is wrong because `ai_query()` runs on Serverless SQL Warehouses, which auto-scale and do not have fixed memory limits like Classic warehouses; switching to Classic would not help and would actually break `ai_query()` (which requires Serverless).
**Source:** Section 4: Assembling and Deploying – Objective 9: Identify batch inference workloads and apply ai_query() — docs.databricks.com (search: "ai_query function Databricks SQL" and "Batch inference AI functions")

---

### Question 56
**Difficulty:** Advanced

A team's custom MCP server (hosted on Databricks Apps) exposes a `query_customer_database()` tool that searches a confidential customer PII database. A security audit requires: (1) all calls to this tool must be logged for compliance, (2) only users with `customer_data_analyst` role can invoke this tool, (3) rate limiting of 100 calls/minute per user must be enforced. Which Databricks component provides all three capabilities?

A) Databricks Secrets — store the customer database credentials as secrets, and implement logging, authorization, and rate limiting as custom Python middleware within the Databricks App's FastAPI code.
B) Unity AI Gateway — all MCP server traffic routes through the Unity AI Gateway, which provides: (1) centralized audit logging of all tool invocations, (2) identity-based access control (only `customer_data_analyst` role can call the tool), and (3) configurable rate limits per user or group.
C) Databricks Workflows — configure a Workflow to run a pre-invocation security check Task before the MCP server tool is called, and a post-invocation logging Task after — Workflows provide sequential task orchestration with built-in retry and audit trail.
D) Unity Catalog row-level security — apply a row filter on the customer PII table that only returns rows when the calling user has `customer_data_analyst` role, and rely on Unity Catalog's query history for audit logging and its connection management for rate limiting.

**Correct Answer:** B
**Explanation:** B is correct. The Unity AI Gateway is the central governance layer for all MCP server traffic in Databricks. It provides exactly the three required capabilities: (1) **Audit logging** — all tool invocations through the Gateway are logged with caller identity, timestamp, tool name, and request/response metadata. (2) **Access control** — Unity AI Gateway policies can enforce identity-based authorization, allowing only users or service principals with specific roles (like `customer_data_analyst`) to invoke specific tools. (3) **Rate limiting** — configurable per-user or per-group rate limits can be set directly in the Gateway configuration. The Gateway intercepts all MCP traffic at the protocol level, enforcing these policies before the request reaches the Databricks App. A is wrong because implementing logging, authorization, and rate limiting as custom Python middleware in the app code is fragile, harder to audit centrally, and bypassed if the MCP server is called directly without going through the middleware. C is wrong because Databricks Workflows are batch/scheduled job orchestrators — they cannot intercept and gate individual real-time MCP tool calls; security policies for real-time API calls require the Unity AI Gateway. D is wrong because Unity Catalog row-level security governs data access at the table query level — it doesn't provide tool-invocation-level rate limiting or structured audit trails for MCP protocol calls.
**Source:** Section 4: Assembling and Deploying – Objective 13: Integrate managed, external, and custom MCP servers — docs.databricks.com (search: "MCP servers Databricks" and "Unity Catalog MCP services")

---

### Question 57
**Difficulty:** Proficiency

A platform engineer is designing the serving infrastructure for a RAG chatbot with these non-functional requirements: (1) 99.9% availability SLA, (2) P99 latency < 300ms, (3) handles 500 concurrent users with spiky traffic (0 to 500 in 30 seconds), (4) new model versions must be deployable in < 5 minutes without downtime. Evaluate whether Provisioned Throughput or pay-per-token endpoints better satisfy each requirement.

A) Pay-per-token satisfies all four requirements better — it scales from zero to 500 concurrent users instantly (serverless auto-scaling), has no fixed capacity constraints, deploys in < 5 minutes, and Databricks guarantees 99.9% availability for all Foundation Model API endpoints.
B) Provisioned Throughput satisfies (1) availability and (4) deployment speed (< 5 minutes via API update), but struggles with (3) spiky traffic (requires over-provisioning for peak load since capacity is fixed) and may or may not meet (2) latency (< 300ms achievable at correct TPS provisioning level). Pay-per-token handles (3) spiky traffic better but offers no P99 latency guarantee for (2) and has shared infrastructure availability risk for (1).
C) Provisioned Throughput satisfies all four requirements — it provides guaranteed capacity (99.9% availability), guaranteed P99 latency (predictable at provisioned TPS), absorbs the 0-to-500 spike through pre-provisioned capacity headroom, and supports < 5-minute hot-swap deployments.
D) Neither endpoint type satisfies all requirements — a hybrid architecture using Provisioned Throughput as a baseline (for low-latency guaranteed requests) with pay-per-token overflow (for traffic spikes) achieves all four requirements simultaneously.

**Correct Answer:** D
**Explanation:** D is correct. Neither endpoint type perfectly satisfies all four requirements alone — a hybrid is optimal: (1) **99.9% availability** → Both types are managed by Databricks. Provisioned Throughput provides more predictable availability since dedicated compute is reserved. A hybrid retains availability via failover. (2) **P99 < 300ms** → Provisioned Throughput with sufficient TPS provisioning can guarantee P99 latency. Pay-per-token has no latency SLA and may spike under load. (3) **0 to 500 in 30 seconds** → Pay-per-token handles spikes (serverless auto-scaling). Provisioned Throughput requires over-provisioning for 500-user peak, which is expensive at 0-user off-peak. A hybrid uses Provisioned Throughput for baseline (e.g., 200 users) and overflows to pay-per-token for spikes (201–500 users). (4) **< 5 min downtime-free deployment** → Both support traffic splitting for zero-downtime deployment; update time is comparable. A is wrong because pay-per-token provides NO P99 latency guarantee — under load, latency can spike significantly. C is wrong because Provisioned Throughput has FIXED capacity — a sudden 0-to-500 spike in 30 seconds with under-provisioned Provisioned Throughput results in throttling and latency degradation; it requires over-provisioning which is costly at low utilization. B is partially correct but doesn't identify the hybrid as the solution. D captures the full nuance.
**Source:** Section 4: Assembling and Deploying – Objective 7: Identify how to serve an LLM application — docs.databricks.com (search: "Databricks Foundation Model APIs" and "Provisioned throughput model serving")

---

### Question 58
**Difficulty:** Proficiency

A team's production RAG application has the following architecture: Databricks Apps (Streamlit front-end) → Model Serving endpoint (pyfunc chain) → Vector Search index (Delta Sync, CONTINUOUS) → Foundation Model API. After 3 months, they need to update ALL of the following: (1) the system prompt (improved instructions), (2) the embedding model (from `bge-small-en` to `bge-large-en` for better quality), (3) the pyfunc chain code (new output parser). List the correct deployment sequence and the risk at each step.

A) (1) Update the prompt in MLflow Prompt Registry → re-assign `production` alias → no downtime. (2) Update embedding model → requires re-embedding ALL documents → rebuild entire Vector Search index (significant downtime risk if not managed carefully). (3) Update pyfunc chain → log new model version → traffic split from old to new version → zero downtime.
B) (1) Redeploy the Databricks App with new prompt hardcoded in Streamlit code → no redeployment of Model Serving endpoint needed. (2) Replace `bge-small-en` with `bge-large-en` in the existing Vector Search index configuration → the index automatically re-embeds all documents in background. (3) Push new pyfunc code to Git → MLflow auto-deploys from Git.
C) All three changes can be deployed atomically by creating a new branch in Git, updating all files, and running `databricks bundle deploy` → this deploys all changes simultaneously with zero downtime because Asset Bundles apply changes transactionally.
D) (1) Update the embedding model FIRST (most impactful) → re-embed all documents → sync new index. Then (2) update pyfunc chain code → deploy. Then (3) update prompt → re-assign alias. The prompt update should always be last because prompts can cause unexpected behavior that masks embedding model issues.

**Correct Answer:** A
**Explanation:** A is correct. The deployment sequence and risks: (1) **Prompt update** → MLflow Prompt Registry alias re-assignment is instant and zero-downtime — application immediately loads the new prompt on the next inference call. Risk: minimal; can be instantly rolled back by re-assigning the alias to the previous version. (2) **Embedding model update** → This is the most operationally complex step. Changing the embedding model requires: (a) deleting the old index or creating a new index with the new model configuration, (b) re-embedding ALL 500K+ documents with the new model, (c) rebuilding the ANN index from scratch. During re-embedding, if the old index is deleted, retrieval fails. Mitigation: create a NEW index with the new model, let it sync fully, update the chain code to point to the new index, traffic split, then delete the old index. Risk: HIGH — downtime risk if not managed with parallel index approach. (3) **Pyfunc chain update** → log new version to Unity Catalog → traffic split (10% → 100%) → zero downtime. Risk: low with canary deployment. B is wrong because embedding model configuration on an existing index cannot simply be swapped; re-indexing is required. C is wrong because `databricks bundle deploy` applies changes to infrastructure resources but does NOT handle the data migration required for re-embedding. D's sequencing is partially valid but the reasoning about "prompt always last" is arbitrary business logic, not a technical requirement.
**Source:** Section 4: Assembling and Deploying – Objectives 5, 8, 12, 14 — docs.databricks.com (search: "Register model Unity Catalog MLflow" and "Create Mosaic AI Vector Search index" and "MLflow Prompt Registry Databricks")

---

### Question 59
**Difficulty:** Proficiency

A developer designs a Managed Agent Memory integration for a customer service agent. Customers return multiple times over days/weeks. Requirements: (1) remember each customer's name and account tier (persists across sessions), (2) remember the issues discussed in the current support session (within session only), (3) all memory must be governed by Unity Catalog access controls (no customer A can read customer B's memory). Which Databricks architecture satisfies all three requirements?

A) Use Managed Agent Memory for (1) cross-session preferences (Unity Catalog-governed, per-user namespaced), LangGraph Checkpointer with Lakebase for (2) within-session conversation history (thread_id = session_id), and (3) Unity Catalog row-level security applied to the Lakebase memory table (filtering rows by customer_id).
B) Use a single Redis cache for all memory — Redis supports both session-scoped TTL keys (for within-session memory) and persistent keys (for cross-session memory), and its Redis ACL feature provides access isolation between customers.
C) Use MLflow Experiment tags for (1) cross-session data (stored as run parameters on the customer's dedicated experiment), and Unity Catalog Delta Lake for (2) session data (each session writes a new row), with (3) access controlled by Unity Catalog table permissions.
D) Use Inference Tables for both (1) and (2) — Inference Tables capture all inputs/outputs and the agent can query the table at session start to reconstruct previous context, with Unity Catalog permissions on the table providing customer isolation.

**Correct Answer:** A
**Explanation:** A is correct. This architecture maps each requirement to the appropriate Databricks component: (1) **Cross-session memory (name, account tier)** → Managed Agent Memory is the purpose-built Databricks service for this — it is Unity Catalog-governed, supports per-user namespaced key-value storage (no customer A can read customer B's namespace), and is fully managed with zero infrastructure. (2) **Within-session conversation history** → LangGraph Checkpointer with Lakebase stores conversation state within a thread_id (= current session ID). When the session ends, the thread's checkpoint remains in Lakebase but is not automatically loaded in the next session. (3) **Unity Catalog governance** → Managed Agent Memory uses UC governance natively. The Lakebase session memory table can have row-level security policies (`WHERE customer_id = current_user_customer_id`) applied via Unity Catalog. B is wrong because Redis is an external SaaS dependency outside the Databricks security perimeter — it doesn't provide Unity Catalog governance and requires separate infrastructure management. C is wrong because MLflow Experiment tags are for ML experiment metadata tracking — using them as a per-customer cross-session memory store is an anti-pattern that scales poorly and lacks proper identity-based access controls. D is wrong because Inference Tables are monitoring tools (logging production traffic) — using them as a memory retrieval system by querying past rows creates high latency at session start and does not provide the structured, indexed memory access pattern needed for production agent memory.
**Source:** Section 4: Assembling and Deploying – Objective 11: Configure a persistent datastore — docs.databricks.com (search: "Agent memory Databricks" and "Lakebase Databricks Postgres")

---

### Question 60
**Difficulty:** Proficiency

A senior engineer reviews a junior developer's implementation of a Vector Search index creation for a real-time news chatbot (knowledge base updated continuously every 30 seconds with breaking news). The junior developer uses:

```python
vsc.create_delta_sync_index(
    endpoint_name="news_vs_endpoint",
    source_table_name="main.news.articles_chunks",
    index_name="main.news.articles_index",
    pipeline_type="TRIGGERED",
    primary_key="chunk_id",
    embedding_source_column="chunk_text",
    embedding_model_endpoint_name="databricks-bge-small-en"
)
```

Identify ALL issues with this configuration for the stated use case and explain the correct configuration.

A) The only issue is the embedding model — `bge-small-en` should be replaced with `bge-large-en` for news content, which has more diverse vocabulary than general text. The `TRIGGERED` pipeline type is acceptable for a 30-second update frequency.
B) Three issues: (1) `pipeline_type="TRIGGERED"` should be `"CONTINUOUS"` — news updates every 30 seconds require near-real-time sync, not manual triggers. (2) `databricks-bge-small-en` may be underpowered for the diverse vocabulary of breaking news — `bge-large-en` provides better semantic coverage. (3) The Vector Search endpoint size `news_vs_endpoint` should be verified to handle the high write throughput from continuous news ingestion, which requires adequate endpoint provisioning.
C) The only issue is the `primary_key` — for news chunks that update frequently, the primary key should be a composite key of `(article_id, chunk_index)` to uniquely identify each chunk within an article; using only `chunk_id` causes update conflicts when existing chunks are modified.
D) There are no issues — `TRIGGERED` with a 30-second manual trigger schedule is equivalent to `CONTINUOUS` mode for practical purposes, and `bge-small-en` is recommended for high-throughput real-time pipelines because its smaller size reduces embedding latency.

**Correct Answer:** B
**Explanation:** B is correct. Multiple issues exist: (1) **`pipeline_type="TRIGGERED"` is critically wrong for this use case.** News updates every 30 seconds — TRIGGERED mode only syncs when explicitly triggered by calling `index.sync()`. Someone must call `sync()` every 30 seconds via a scheduled job, adding orchestration complexity. More importantly, each sync call itself takes time to process — if the sync takes longer than 30 seconds, articles are permanently delayed. CONTINUOUS mode is the correct choice: it monitors CDF continuously and processes changes as they arrive, achieving near-real-time freshness without manual orchestration. (2) **`databricks-bge-small-en` may be insufficient** — `bge-small-en` (33M parameters) is optimized for speed over accuracy. For news content with diverse, rapidly evolving vocabulary (breaking events, new names, technical jargon), `bge-large-en` (335M parameters) provides significantly better semantic representation for retrieval quality. (3) **Endpoint provisioning** — continuous high-frequency ingestion from a real-time news pipeline requires adequate Vector Search endpoint compute; an undersized endpoint creates a bottleneck. A is wrong because it accepts `TRIGGERED` as appropriate — for a 30-second update cycle, TRIGGERED is operationally incorrect. D is wrong because TRIGGERED and CONTINUOUS are NOT equivalent — TRIGGERED requires explicit API calls to trigger sync, cannot react automatically to new data, and has higher operational overhead.
**Source:** Section 4: Assembling and Deploying – Objectives 8 & 10: Key concepts and configuration of Mosaic AI Vector Search — docs.databricks.com (search: "Mosaic AI Vector Search overview" and "Mosaic AI Vector Search configuration")
