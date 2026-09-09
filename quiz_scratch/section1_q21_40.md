### Question 21
**Difficulty:** Beginner

A data engineer is asked to build a chatbot for a retail company's internal FAQ. Users will type questions in natural language and expect plain-text conversational answers based on the company's product manuals. Which task type should the engineer configure the model for?

A) Text Classification — because it assigns the user's question to a category like 'shipping', 'returns', or 'products', which then triggers a static pre-written answer for each category.
B) Information Extraction — because it parses the user's question to identify key entities like product names and dates, then returns those entities as structured output for downstream processing.
C) Question Answering / Chat — because it takes a natural language question and returns a natural language answer, optionally grounded in retrieved context from the product manuals via RAG.
D) Text Summarization — because it condenses the product manuals into shorter documents that the user can read directly instead of asking questions to a chatbot.

**Correct Answer:** C
**Explanation:** C is correct. Question Answering / Chat is the task type for systems where users ask free-form natural language questions and expect conversational, natural language answers. When grounded in private documents (product manuals), this becomes a RAG chatbot, the canonical use case for this task type on Databricks. A is wrong because classification only assigns a label to the input — it does not generate an answer. A static response system is not a chatbot. B is wrong because information extraction produces structured output (key-value pairs, entities), not a conversational answer — it's designed to populate databases, not to have dialogues. D is wrong because summarization is a one-time document condensing task performed on the manuals themselves, not an interactive user-facing Q&A system.
**Source:** Section 1: Design Applications – Objective 2: Select model tasks to accomplish a given business requirement — docs.databricks.com (search: "AI Functions on Databricks")

---

### Question 22
**Difficulty:** Beginner

When building a RAG chain on Databricks, which component is responsible for converting a user's text query into a vector so that semantically similar document chunks can be found?

A) The Prompt Template — it formats the user query and retrieved documents into a single string, which implicitly creates a vector representation used by the LLM for retrieval.
B) The Output Parser — it converts the LLM's generated text output into a structured format and uses the schema definition to embed the original query for similarity matching.
C) The Retriever backed by Databricks Vector Search — it uses an embedding model to convert the user query into a vector, then searches the index for chunks with the highest cosine similarity.
D) The LLM (Databricks Model Serving endpoint) — it internally embeds the user query as part of its attention mechanism and uses those internal embeddings to select relevant documents.

**Correct Answer:** C
**Explanation:** C is correct. The Retriever component (e.g., `DatabricksVectorSearch` retriever in LangChain) handles the query-to-vector conversion using a designated embedding model, then queries the Vector Search index for the most semantically similar document chunks. This is its primary and exclusive role in the chain. A is wrong because the Prompt Template is a text formatting component — it assembles the query and retrieved documents into a string for the LLM, and does not perform any embedding or retrieval. B is wrong because the Output Parser operates on the LLM's response at the end of the chain; it has no involvement in the retrieval phase. D is wrong because the LLM's internal attention mechanism is used for generation, not for searching an external document index; the LLM does not access the Vector Search index directly.
**Source:** Section 1: Design Applications – Objective 3: Select chain components – docs.databricks.com (search: "Build a RAG application with Mosaic AI Vector Search")

---

### Question 23
**Difficulty:** Beginner

A developer logs a model using `mlflow.langchain.log_model()` without providing a `signature` or `input_example`. They then try to register it to Unity Catalog with `mlflow.register_model()`. What is the most likely result?

A) The registration succeeds and the model is deployed to a serving endpoint, but the endpoint operates in "schema-less" mode where any payload structure is accepted without validation.
B) The registration fails because Unity Catalog's Model Registry requires all registered models to include an MLflow Model Signature defining the input and output schema.
C) The registration succeeds but the model is placed in a quarantine state in Unity Catalog where it cannot be deployed until a signature is added in a post-registration step.
D) MLflow automatically generates a default signature with `input: string, output: string` when none is provided, allowing registration and deployment to proceed with minimal validation.

**Correct Answer:** B
**Explanation:** B is correct. Unity Catalog enforces that all registered models include an MLflow Model Signature. Without one, the `register_model()` call raises an `MlflowException` about missing schema. The developer must re-log the model with a `signature` (created via `mlflow.models.infer_signature()` or defined manually) or provide an `input_example` so MLflow can auto-infer the signature. A is wrong because Unity Catalog does not have a "schema-less" mode — the signature requirement is strictly enforced for governance and payload validation purposes. C is wrong because there is no quarantine state for models; the registration either succeeds with a valid signature or fails outright. D is wrong because MLflow does not auto-generate a default signature; it only infers one if the developer explicitly provides an `input_example`.
**Source:** Section 1: Design Applications – Objective 4: Translate business goals into inputs/outputs – docs.databricks.com (search: "MLflow Model Signatures")

---

### Question 24
**Difficulty:** Beginner

A developer wants to use the Mosaic AI Agent Framework to build an agent that can answer questions about inventory from a SQL warehouse. They write a Python function that queries the warehouse and want the agent to use it as a tool. Where should this function be registered so the agent can call it in a governed, production-ready way?

A) As a Python file in a Databricks Repo, with the file path provided to the agent's tool configuration so it can import and execute the function directly from the repository at runtime.
B) As a Databricks Workflow Job, triggered by the agent whenever it needs to run the inventory query, with the job's run ID passed back to the agent as the tool's return value.
C) As a Unity Catalog Function using `CREATE FUNCTION` or the Python SDK, which makes the function a governed, versioned, and discoverable tool the agent can call via the Mosaic AI Agent Framework.
D) As a Databricks Secret, where the function's code is stored as an encrypted string that the agent decrypts and executes using Python's `exec()` function at runtime.

**Correct Answer:** C
**Explanation:** C is correct. In the Mosaic AI Agent Framework, tools are registered as Unity Catalog Functions. This provides governance (access control via UC permissions), versioning, and discoverability. The agent is given the list of UC Function names and the LLM decides when to call them. A is wrong because executing arbitrary Python files from repos at runtime is not the supported tool mechanism in the Agent Framework — it's ungoverned and not discoverable. B is wrong because Databricks Workflow Jobs are batch pipeline orchestration tools, not an agent tool calling mechanism; the async nature of job execution is incompatible with the agent's synchronous tool call-response loop. D is wrong because Databricks Secrets are for storing credentials (API keys, passwords), not executable code; executing code stored in secrets via `exec()` is a serious security anti-pattern.
**Source:** Section 1: Design Applications – Objective 5: Define and order tools for multi-stage reasoning – docs.databricks.com (search: "Create tools for agents using Unity Catalog functions")

---

### Question 25
**Difficulty:** Beginner

A company wants to automatically convert scanned call transcripts (plain text) into structured rows in a Delta table, capturing fields like `customer_name`, `issue_type`, `resolution_status`, and `call_duration_minutes`. Which Agent Brick and/or AI function is most appropriate?

A) Knowledge Assistant with `ai_summarize()` — the Knowledge Assistant retrieves relevant transcripts from Vector Search, and `ai_summarize()` condenses them into the four required fields.
B) Multiagent Supervisor with a dedicated SQL Agent — the Supervisor routes each transcript to the SQL Agent, which uses standard SQL string functions to parse and extract the structured fields.
C) Information Extraction using `ai_extract()` — it parses each unstructured transcript and extracts the named fields (`customer_name`, `issue_type`, etc.) into a structured schema written to a Delta table.
D) Function Calling Agent with `ai_classify()` — the agent classifies each transcript by `issue_type` and then uses conditional tool calls to populate the remaining three fields based on the classification result.

**Correct Answer:** C
**Explanation:** C is correct. Information Extraction using `ai_extract()` is specifically designed for this scenario: converting unstructured text (transcripts) into structured fields by specifying a target schema. The output is a STRUCT type that can be written directly to a Delta table as columns. A is wrong because `ai_summarize()` produces a free-text summary paragraph, not structured key-value fields; a Knowledge Assistant is for Q&A, not batch ETL extraction. B is wrong because a Multiagent Supervisor adds unnecessary orchestration complexity, and SQL string functions cannot reliably extract semantic entities like `customer_name` or `resolution_status` from free-form transcript text. D is wrong because `ai_classify()` assigns a single category label to the whole text — it does not extract multiple structured fields; using it for `issue_type` alone and patching the rest with conditional tool calls is fragile and overly complex.
**Source:** Section 1: Design Applications – Objective 6: Determine how and when to use Agent Bricks – docs.databricks.com (search: "Parse and extract data with ai_extract")

---

### Question 26
**Difficulty:** Intermediate

A developer's production chain uses `JsonOutputParser` but the LLM occasionally wraps JSON in markdown fences (` ```json ... ``` `), causing `OutputParserException`. The team wants the most reliable fix that avoids changing the parser class. What should they do?

A) Add `"temperature": 0` to the LLM call parameters to make output deterministic, which eliminates formatting variation and prevents the model from adding markdown code fences.
B) Switch from `JsonOutputParser` to `StrOutputParser` and add a custom `strip_markdown_json()` helper function that uses regex to remove fences before calling `json.loads()`.
C) Inject an explicit negative instruction into the system prompt: "Return ONLY the raw JSON object. Do NOT wrap it in markdown code fences, backticks, or any other formatting characters."
D) Move the model call to a new Databricks Model Serving endpoint configured with the `response_format: json_object` parameter, which enforces JSON-only output at the API layer.

**Correct Answer:** C
**Explanation:** C is correct. Adding a specific negative instruction directly addresses the root cause — the model's default tendency to wrap code in markdown. This is the targeted fix that keeps `JsonOutputParser` in place and has immediate effect with zero architectural changes. A is wrong because `temperature=0` controls output randomness, not formatting behavior like adding markdown fences; deterministic output can still consistently produce fenced JSON. B is wrong because it replaces the parser and adds custom string manipulation code — it works but abandons the structured parser and is more error-prone. D is wrong because while some models support `response_format: json_object`, this is a model-specific API feature not universally available on all Databricks Foundation Model API endpoints, making it less portable than a prompt fix.
**Source:** Section 1: Design Applications – Objective 1: Design a prompt that elicits a specifically formatted response – docs.databricks.com (search: "Query generative AI models Foundation Model APIs")

---

### Question 27
**Difficulty:** Intermediate

A legal technology company has 300,000 contracts in a Delta table. They need to label each contract with one of five types: NDA, MSA, SOW, SLA, or Purchase Order. No field extraction is needed — only the type label. Which is the most efficient approach on Databricks?

A) Build a LangChain chain with a `ChatDatabricks` LLM, ask it to return the contract type as a string, and run it as a Spark UDF across all 300,000 rows using `mapInPandas`.
B) Use `ai_classify()` in a Databricks SQL query against the Delta table, specifying the five label options, and process the full dataset in a single serverless SQL warehouse batch job.
C) Use `ai_extract()` with a schema that defines a single `contract_type` field, running it across the Delta table to populate the label column from the unstructured contract text.
D) Fine-tune a small BERT-based classification model on labeled contract examples, deploy it to a Databricks Model Serving endpoint, and call it via a batch `ai_query()` SQL function.

**Correct Answer:** B
**Explanation:** B is correct. `ai_classify()` is the Databricks SQL AI function purpose-built for multi-class text labeling. It accepts a list of target categories and returns the predicted label. Running it as a batch SQL query on a serverless warehouse is the most efficient, lowest-complexity approach for this bulk classification task. A is wrong because using a Spark UDF with a LangChain chain involves significantly more code, higher latency per row, and more operational complexity than the native SQL AI function — it reinvents what `ai_classify()` already does. C is wrong because `ai_extract()` is for extracting specific data fields from text; using it for single-field classification is the wrong tool, and it would return a STRUCT instead of a simple label string. D is wrong because fine-tuning a custom model is a heavyweight, time-consuming solution for a problem that `ai_classify()` solves directly without any model training.
**Source:** Section 1: Design Applications – Objective 2: Select model tasks – docs.databricks.com (search: "AI Functions on Databricks ai_classify")

---

### Question 28
**Difficulty:** Intermediate

A RAG chain is returning low-quality answers even though the Vector Search index contains the correct information. Investigation reveals the retriever returns 10 chunks, but the most relevant chunk is consistently ranked 7th or 8th. What component should be inserted between the Retriever and the Prompt Template?

A) A second `ChatDatabricks` LLM call that reads all 10 chunks and re-writes them in order of relevance before they are passed to the Prompt Template for final answer generation.
B) A `StrOutputParser` component that converts the list of `Document` objects into a ranked string, using the document metadata score field to sort them before prompt assembly.
C) A reranker (cross-encoder model) that jointly scores each retrieved chunk against the user query and reorders the chunks so the most relevant ones appear first before prompt assembly.
D) A second Vector Search query with a higher `num_results` value (e.g., 50 instead of 10) to cast a wider retrieval net, increasing the probability that the most relevant chunk appears in the top 3.

**Correct Answer:** C
**Explanation:** C is correct. A reranker uses a cross-encoder model that evaluates query-document pairs together (not independently like the initial bi-encoder retrieval), producing much more accurate relevance scores. Inserting it between the Retriever and Prompt Template reorders the chunks so the most relevant appear first, directly fixing the ranking quality issue. A is wrong because using a second LLM call to reorder chunks is expensive, slow, and introduces hallucination risk — the LLM may misjudge relevance or alter the chunk content. B is wrong because `StrOutputParser` is a text parsing component that converts LLM output strings, not a document ranking component; metadata similarity scores from vector search are not the same as cross-encoder relevance scores. D is wrong because retrieving more chunks with a wider search doesn't fix the ranking problem — the most relevant chunk will still be buried, and now there's more irrelevant context to confuse the LLM.
**Source:** Section 1: Design Applications – Objective 3: Select chain components – docs.databricks.com (search: "Build a RAG application with Mosaic AI Vector Search")

---

### Question 29
**Difficulty:** Intermediate

A team provides `input_example={"query": "What is our PTO policy?", "chat_history": []}` when calling `mlflow.langchain.log_model()`. They do not manually create a signature. What does MLflow do with this `input_example` at log time?

A) MLflow stores the `input_example` as a sample request in the model artifact for documentation purposes only; the developer must still call `mlflow.models.infer_signature()` separately to create the actual signature.
B) MLflow runs the model against the `input_example` at log time, captures the actual model output, and uses both the input and output shapes to automatically infer and attach a `ModelSignature` to the logged artifact.
C) MLflow stores the `input_example` in the MLflow tracking server as an experiment artifact tag, but it is not used for signature inference; it only appears in the MLflow UI for human reference.
D) MLflow converts the `input_example` into an OpenAPI JSON schema and attaches it to the model artifact, which the Databricks Model Serving endpoint uses instead of an MLflow Model Signature.

**Correct Answer:** B
**Explanation:** B is correct. When `input_example` is provided to `log_model()`, MLflow automatically runs the model against it, captures the resulting output, and calls `infer_signature()` internally on the input/output pair to generate and attach a `ModelSignature` to the logged model. This is the recommended shortcut that avoids manually calling `infer_signature()`. A is wrong because `input_example` does more than documentation — it actively triggers signature auto-inference when provided, which is its primary purpose. C is wrong because `input_example` is not just a tag; it is a functional input that triggers signature inference and is also stored as a sample payload in the model artifact directory. D is wrong because MLflow does not generate OpenAPI schemas from `input_example`; it generates a native MLflow `ModelSignature` object with a Databricks-native schema format.
**Source:** Section 1: Design Applications – Objective 4: Translate business goals into inputs/outputs – docs.databricks.com (search: "MLflow model signature input example")

---

### Question 30
**Difficulty:** Intermediate

A Mosaic AI Agent is given three tools: `get_product_info` (read), `check_stock` (read), and `place_order` (write/action). A user says: "Order 50 units of Product A if it's in stock." In what sequence should the agent call these tools, and what principle governs this?

A) The agent should call `place_order` first as a reservation hold, then `check_stock` to verify availability, then `get_product_info` to confirm the product details — prioritizing speed of action over information gathering.
B) The agent should call all three tools in parallel simultaneously to minimize latency, then reconcile the results afterward before deciding whether the order should proceed or be cancelled.
C) The agent should call `get_product_info` first to confirm Product A exists, then `check_stock` to verify inventory, then conditionally call `place_order` only if stock is sufficient — knowledge before action.
D) The agent should call `check_stock` and `place_order` in sequence automatically, as the Mosaic AI Agent Framework enforces alphabetical tool execution order when multiple tools are registered.

**Correct Answer:** C
**Explanation:** C is correct. The core principle is "knowledge before action": read-type tools (gathering information) must precede write/action tools (causing side effects). The agent first confirms the product exists, then checks stock — both are prerequisite knowledge. Only after both conditions are verified does the agent conditionally call `place_order`. This prevents irreversible actions based on incomplete information. A is wrong because placing an order before confirming stock could result in ordering a product that doesn't exist or is out of stock — a costly error. B is wrong because parallel execution prevents the agent from using the result of one tool to conditionally decide whether to call the next; this breaks the conditional logic required by "only order if in stock." D is wrong because the Mosaic AI Agent Framework does not enforce alphabetical ordering; the LLM dynamically determines which tool to call and when based on the task requirements.
**Source:** Section 1: Design Applications – Objective 5: Define and order tools for multi-stage reasoning – docs.databricks.com (search: "Mosaic AI Agent Framework")

---

### Question 31
**Difficulty:** Advanced

A developer builds a multi-turn RAG chatbot in LangChain on Databricks. Without any modifications to the retriever, users report that follow-up questions like "Tell me more about the second point" return irrelevant documents. What is missing from the chain, and what is the fix?

A) The chain is missing a second Vector Search index optimized for conversational queries; the fix is to create a separate index with shorter chunk sizes specifically for follow-up questions.
B) The chain is missing a `ConversationalRetrievalChain` or equivalent history-aware retrieval step that rewrites the follow-up question using `chat_history` context before passing it to the retriever.
C) The chain is missing a `PydanticOutputParser` to enforce that follow-up question responses are structured consistently, which would allow the retriever to recognize the query pattern and return better results.
D) The chain is missing a rate-limiter on the Vector Search index; without it, rapid follow-up queries time out and return irrelevant fallback documents instead of the correct ones.

**Correct Answer:** B
**Explanation:** B is correct. Follow-up questions like "Tell me more about the second point" are context-dependent — they refer to something from the previous turn. Without `chat_history`, the retriever receives a decontextualized query and cannot find relevant documents. A `ConversationalRetrievalChain` or a history-aware retriever rewrites the follow-up question into a standalone query (e.g., "Tell me more about [specific topic from previous answer]") using the conversation history before sending it to the retriever. A is wrong because the issue is not index granularity — a second index with shorter chunks doesn't solve decontextualized queries; the retriever still receives an unresolved reference. C is wrong because `PydanticOutputParser` operates on the LLM's output, not on the retrieval step; output formatting has no effect on retrieval relevance. D is wrong because rate-limiting protects against abuse, not retrieval quality; the described issue is a query context problem, not a throughput problem.
**Source:** Section 1: Design Applications – Objective 3: Select chain components – docs.databricks.com (search: "Log and load LangChain models with MLflow")

---

### Question 32
**Difficulty:** Advanced

A data platform team registers two separate LangChain chains to Unity Catalog: `prod.nlp.summarizer` (input: `{text: string}`, output: `string`) and `prod.nlp.extractor` (input: `{text: string}`, output: `{entities: array<string>}`). Can they share one MLflow Model Signature? Why or why not?

A) Yes — they can share one signature because both chains accept the same input schema `{text: string}`, and MLflow signatures only validate inputs, not outputs, at serving time.
B) No — they cannot share a signature because MLflow Model Signatures must be unique per model registration and Unity Catalog prevents two models from referencing the same signature object.
C) No — they cannot share a signature because `summarizer` outputs a `string` and `extractor` outputs `{entities: array<string>}`. A signature includes both input AND output schema, and these output schemas are different.
D) Yes — they can share a signature if the team registers them with the same `registered_model_name`, which collapses both chains into separate versions of one model with one shared schema.

**Correct Answer:** C
**Explanation:** C is correct. An MLflow Model Signature defines BOTH the input schema and the output schema. The two chains have the same inputs but different outputs — `string` vs `{entities: array<string>}`. They cannot share a single signature because the output definitions are incompatible. Each chain must be logged with its own distinct signature that accurately reflects its output contract. A is wrong because MLflow signatures validate BOTH inputs AND outputs at the serving endpoint — not just inputs. B is wrong because MLflow signatures are not database objects with uniqueness constraints; the reason sharing is impossible here is schema incompatibility, not a registry policy. D is wrong because registering under the same model name creates versions of the same model, which implies a compatible and consistent schema — combining chains with different output schemas under one model name would break the schema contract for callers.
**Source:** Section 1: Design Applications – Objective 4: Translate business goals into inputs/outputs – docs.databricks.com (search: "MLflow Model Signatures")

---

### Question 33
**Difficulty:** Advanced

A developer uses `mlflow.models.infer_signature(model_input, model_output)` where `model_input` is a pandas DataFrame and `model_output` is a list of strings. What does `infer_signature()` actually analyze to build the schema?

A) `infer_signature()` inspects the model object's Python class definition and source code to determine what data types the model was designed to accept and return, independent of the sample data.
B) `infer_signature()` calls the model's `/invocations` REST endpoint with the sample input and parses the HTTP response headers to extract the declared input/output content types.
C) `infer_signature()` analyzes the Python types, shapes, and column names of the provided `model_input` and `model_output` sample data objects to construct the schema — it does not inspect the model itself.
D) `infer_signature()` reads the model's MLflow `tags` dictionary for keys prefixed with `schema_` and converts those tag values into the input and output schema definition.

**Correct Answer:** C
**Explanation:** C is correct. `infer_signature()` is a pure data introspection function — it examines the structure of the sample `model_input` (e.g., a pandas DataFrame's column names and dtypes) and `model_output` (e.g., a list of strings) to construct the `ModelSignature`. It does not execute the model, read source code, or inspect the model object itself. A is wrong because `infer_signature()` does not perform code introspection or static analysis of the model class — it only looks at the provided sample data objects. B is wrong because `infer_signature()` works entirely locally in Python memory; it never makes any HTTP calls or interacts with a REST endpoint. D is wrong because MLflow tags are free-form metadata strings for tracking; `infer_signature()` does not read or parse tags.
**Source:** Section 1: Design Applications – Objective 4: Translate business goals into inputs/outputs – docs.databricks.com (search: "MLflow model signature infer_signature")

---

### Question 34
**Difficulty:** Advanced

An agent built with the Mosaic AI Agent Framework uses a Unity Catalog Function tool called `query_hr_data`. The agent's service principal has `EXECUTE` privilege on the function, but users report the agent returns empty results for certain employees. Investigation shows the `hr_employees` table referenced by the function has a row-level filter policy applied in Unity Catalog. What is happening?

A) The `EXECUTE` privilege on the function is being blocked by the row-level filter — a known conflict where Unity Catalog cannot apply row filters to functions called by service principals.
B) The row-level filter is working correctly: it is restricting the rows the agent's service principal can see based on its identity, returning only the data the service principal is authorized to access.
C) The row-level filter is a bug in this scenario — Unity Catalog row filters only apply to direct SQL queries, not to data accessed through Unity Catalog Functions called by an agent.
D) The service principal needs `SELECT` privilege on the `hr_employees` table in addition to `EXECUTE` on the function, as row-level filters are bypassed entirely when access is through a UC Function.

**Correct Answer:** B
**Explanation:** B is correct. This is Unity Catalog governance working as designed. Row-level filter policies on a table apply to ALL access paths — including access through Unity Catalog Functions. The filter evaluates the identity of the calling service principal and restricts the result set to only the rows that identity is authorized to see. "Empty results" for certain employees means the filter correctly determined the agent's service principal is not authorized to view those records. A is wrong because there is no known conflict between row filters and UC Function execution — they work together by design. C is wrong because row-level filters in Unity Catalog apply universally to all access patterns, including indirect access through Functions; they are not limited to direct SQL queries. D is wrong because the `EXECUTE` privilege on the function is sufficient for function invocation; the row filter is not bypassed — it is actively and correctly restricting the rows returned.
**Source:** Section 1: Design Applications – Objective 5: Define and order tools for multi-stage reasoning – docs.databricks.com (search: "Unity Catalog row filters")

---

### Question 35
**Difficulty:** Advanced

A Multiagent Supervisor routes a user's question to either a Document Agent (searches PDFs) or a SQL Agent (queries Delta tables). A user asks: "What were last quarter's sales figures, and how does that compare with our pricing policy?" The supervisor must route correctly. What is the ideal behavior?

A) The supervisor routes the entire query to the SQL Agent because it can answer numeric questions about sales figures, and numeric grounding is always prioritized over document retrieval for factual queries.
B) The supervisor recognizes the query spans two domains and routes it to both agents — the SQL Agent for sales figures and the Document Agent for pricing policy — then synthesizes their responses into a unified answer.
C) The supervisor routes to the Document Agent first because pricing policy documents are more authoritative than database records, then asks the SQL Agent to validate the figures mentioned in the policy documents.
D) The supervisor cannot handle queries that span multiple domains and returns an error, requiring the user to split the question into two separate queries directed to each specialized agent.

**Correct Answer:** B
**Explanation:** B is correct. This is the primary value of the Multiagent Supervisor pattern: it can recognize that a single user query spans multiple knowledge domains and route sub-tasks to multiple specialized agents in parallel or sequence. The SQL Agent fetches the quantitative sales data, the Document Agent retrieves the pricing policy, and the Supervisor synthesizes both into a coherent answer. A is wrong because "always prioritize numeric/SQL" is not a correct routing principle — the query explicitly requires both structured data AND document retrieval; routing to only one agent would give an incomplete answer. C is wrong because priority-based routing (pricing policy over DB) doesn't reflect the user's actual intent, which requires both data types; the routing should be based on information need, not perceived authority. D is wrong because handling cross-domain queries is the explicit purpose of the Multiagent Supervisor — routing to multiple agents simultaneously is exactly what it is designed to do.
**Source:** Section 1: Design Applications – Objective 6: Determine how and when to use Agent Bricks – docs.databricks.com (search: "Mosaic AI Agent Framework tutorials")

---

### Question 36
**Difficulty:** Proficiency

A developer uses `PydanticOutputParser` with a Pydantic model that has `class Config: extra = 'forbid'`. The LLM occasionally returns JSON with an extra `debug_info` field not in the schema. What happens, and what is the correct architectural fix?

A) The parser silently ignores the `debug_info` field because `JsonOutputParser` (which `PydanticOutputParser` internally delegates to) strips unknown keys before Pydantic validation runs.
B) The parser raises a Pydantic `ValidationError` because `extra = 'forbid'` causes Pydantic to reject any JSON containing keys not declared in the model — the fix is to add a `.with_retry()` call or change `extra` to `'ignore'`.
C) The serving endpoint intercepts the extra field before it reaches the parser, and the MLflow Model Signature validation removes undeclared fields from the LLM output payload automatically.
D) The `OutputParserException` is raised, but only in production serving — in local notebook testing, `PydanticOutputParser` accepts extra fields regardless of the `extra = 'forbid'` config setting.

**Correct Answer:** B
**Explanation:** B is correct. Pydantic's `extra = 'forbid'` setting means ANY key in the JSON that is not explicitly declared in the model raises a `ValidationError`. The LLM adding `debug_info` triggers this every time. The architectural fix is to change `Config.extra = 'ignore'` (which silently drops undeclared fields) if the extra field is harmless, OR to strengthen the system prompt with "Return ONLY the fields defined in the schema: [field list]. Do not add any additional fields." A is wrong because `PydanticOutputParser` does NOT internally delegate to `JsonOutputParser` in a way that strips fields; it passes the full JSON string to the Pydantic model for direct validation. C is wrong because MLflow Model Signatures validate the input/output schema of the overall chain, not the internal JSON fields within the LLM's text response; signatures do not filter fields inside the response text. D is wrong because Pydantic validation is pure Python logic — `extra = 'forbid'` behaves identically in notebooks and in production serving; there is no environment-specific difference.
**Source:** Section 1: Design Applications – Objective 1: Design a prompt that elicits a specifically formatted response – docs.databricks.com (search: "MLflow LangChain flavor")

---

### Question 37
**Difficulty:** Proficiency

An enterprise AI team deploys a Mosaic AI Agent using `agents.deploy()`. Six months later, the underlying Unity Catalog Function tool `get_customer_data` is updated by the data engineering team — a new column `lifetime_value` is added to its return schema. Does the deployed agent automatically reflect this change? What is the risk?

A) Yes — the agent automatically reflects the change because Unity Catalog Functions are dynamic references; the agent always calls the latest version of the function at runtime with no redeployment needed, and the new column appears in responses.
B) No — `agents.deploy()` creates a snapshot of the function definition at deployment time; the agent uses the cached schema, so the new column is invisible until the agent is redeployed with the updated function reference.
C) Yes — but with risk: the agent calls the current live version of the function and receives the new `lifetime_value` column, but if the agent's MLflow signature does not account for this new output field, downstream consumers may encounter schema validation errors.
D) No — Unity Catalog Functions are immutable once deployed; the data engineering team must create a new function version (e.g., `get_customer_data_v2`) and the agent must be reconfigured to use the new version name before any changes take effect.

**Correct Answer:** C
**Explanation:** C is correct. Unity Catalog Functions are live references — the deployed agent calls the current version of the function at runtime, so it will receive the new `lifetime_value` column immediately after the function is updated. The risk is downstream schema drift: if the agent's MLflow Model Signature or downstream application code doesn't account for the new output field, consumers may encounter unexpected data or validation failures. The team should update the agent's signature and redeploy to formally capture the new output contract. A is wrong because it correctly identifies that the change is reflected dynamically, but understates the risk of undocumented schema drift — calling it risk-free is incorrect. B is wrong because `agents.deploy()` does not snapshot function definitions; functions are called live at runtime. D is wrong because Unity Catalog Functions are not immutable after deployment; they can be updated or replaced, and the agent calls whatever the current definition is.
**Source:** Section 1: Design Applications – Objective 5: Define and order tools for multi-stage reasoning – docs.databricks.com (search: "Mosaic AI Agent Framework")

---

### Question 38
**Difficulty:** Proficiency

A developer is choosing between `StrOutputParser` and `JsonOutputParser` for a chain that produces product recommendations as a numbered list in plain text (e.g., "1. Product A\n2. Product B"). The downstream consumer is a human-readable dashboard that displays the text directly. Which parser is correct and why?

A) `JsonOutputParser` is correct because it is more robust for production systems — it validates that the output conforms to a standard format, preventing any unexpected characters or formatting from reaching the dashboard.
B) `StrOutputParser` is correct because the LLM output is plain text (a numbered list), not JSON. `StrOutputParser` simply passes the raw string through without attempting JSON deserialization, which would fail on this format.
C) `JsonOutputParser` is correct because Databricks dashboards require JSON-formatted data to render correctly, and `JsonOutputParser` will automatically convert the numbered list into a JSON array for dashboard consumption.
D) Neither parser is suitable — a custom `ListOutputParser` must be implemented to correctly parse numbered lists into Python list objects before the data can be rendered on a Databricks dashboard.

**Correct Answer:** B
**Explanation:** B is correct. `StrOutputParser` is the right choice when the desired output is a plain text string and no further parsing or structure validation is needed. It simply returns the LLM's raw text output unchanged, which is exactly what a human-readable plain-text dashboard requires. A is wrong because `JsonOutputParser` would attempt to parse the numbered list as JSON and throw an `OutputParserException` since "1. Product A\n2. Product B" is not valid JSON. B handles the text correctly. C is wrong because Databricks dashboards can render plain text strings directly; `JsonOutputParser` cannot magically convert a numbered list into a JSON array. D is wrong because for plain text output displayed directly to humans, `StrOutputParser` is both suitable and the simplest correct choice; a custom parser adds unnecessary complexity.
**Source:** Section 1: Design Applications – Objective 3: Select chain components – docs.databricks.com (search: "Build a RAG application with Mosaic AI Vector Search")

---

### Question 39
**Difficulty:** Proficiency

A platform team wants to expose a "summarize contract" LLM capability to 20 internal applications. They are debating between: (Option A) each application calls the Foundation Model API directly with a shared system prompt stored in Databricks Secrets, or (Option B) one MLflow pyfunc model is logged with the system prompt embedded, registered to Unity Catalog, and deployed as a shared Model Serving endpoint. What is the key governance advantage of Option B?

A) Option B is faster because Model Serving endpoints use GPU-optimized inference hardware that is shared across all 20 callers, whereas direct Foundation Model API calls use CPU-only compute for each individual application.
B) Option B centralizes governance: all 20 applications call one versioned, Unity Catalog-governed endpoint. Prompt updates, model swaps, and access control changes are made once at the endpoint level without touching any application code.
C) Option B is cheaper because Databricks charges a lower per-token rate for calls made through a registered MLflow model endpoint compared to direct Foundation Model API calls from application code.
D) Option B provides better output quality because the MLflow pyfunc wrapper applies automatic response quality scoring using built-in MLflow judges before returning results to the calling application.

**Correct Answer:** B
**Explanation:** B is correct. The key governance advantage of a shared Model Serving endpoint is centralization: one registered, versioned model in Unity Catalog serves all 20 applications. Access is controlled via Unity Catalog `CAN QUERY` permissions. When the prompt needs updating or the underlying model is swapped (e.g., from Llama 3 70B to a newer model), only the endpoint is redeployed — no changes needed in any of the 20 applications. This is the governance, versioning, and operational efficiency argument for the shared endpoint approach. A is wrong because Model Serving endpoints do use GPU-optimized infrastructure, but this is a performance/cost claim, not a governance claim — and direct Foundation Model API calls also use Databricks-managed GPU infrastructure. C is wrong because there is no published Databricks pricing tier that offers a discount for calls routed through a registered MLflow model vs. direct API calls. D is wrong because MLflow pyfunc wrappers do not automatically apply quality scorers to every production response; quality evaluation is a separate, explicit step.
**Source:** Section 1: Design Applications – Objective 4: Translate business goals into inputs/outputs – docs.databricks.com (search: "Register model Unity Catalog MLflow")

---

### Question 40
**Difficulty:** Proficiency

A company uses a Multiagent Supervisor where the Supervisor LLM routes to a SQL Agent or a Document Agent. During a security audit, it is discovered that both sub-agents can access each other's data sources — the SQL Agent can retrieve PDF documents and the Document Agent can run SQL queries. What design flaw caused this, and how should it be fixed?

A) The flaw is that the Mosaic AI Agent Framework does not support access isolation between sub-agents; the only fix is to deploy each sub-agent as a completely separate Databricks workspace with its own Unity Catalog metastore.
B) The flaw is that all sub-agents were deployed under the same service principal identity, giving each agent access to all tools registered to that identity; the fix is to give each sub-agent its own dedicated service principal with only the UC permissions it needs.
C) The flaw is in the Supervisor's routing prompt — it fails to instruct sub-agents to ignore tools outside their domain; the fix is to add a sentence like "You may only use tools in your assigned category" to each sub-agent's system prompt.
D) The flaw is that Unity Catalog Function tools cannot be scoped to individual agents within a Multiagent Supervisor; this is a known platform limitation requiring a third-party access control layer like AWS IAM.

**Correct Answer:** B
**Explanation:** B is correct. If all sub-agents run under the same service principal, they inherit the same Unity Catalog permissions — meaning the SQL Agent's service principal has `EXECUTE` on both SQL tools AND document retrieval functions. The correct fix is the principle of least privilege: each sub-agent should run under its own dedicated service principal, and each service principal is granted `EXECUTE` only on the specific Unity Catalog Functions relevant to its domain. A is wrong because workspace isolation is an extreme overengineering of the solution; service principal isolation achieves the same security goal with much less operational overhead. C is wrong because system prompt instructions are a soft guardrail — a prompt-injected user could override them; Unity Catalog permissions are hard technical controls that cannot be bypassed through prompt manipulation. D is wrong because Unity Catalog Functions CAN be scoped by identity; this is a core UC feature, not a platform limitation.
**Source:** Section 1: Design Applications – Objective 5 & 6: Multi-stage reasoning and Agent Bricks – docs.databricks.com (search: "Unity Catalog permissions Model Serving")
