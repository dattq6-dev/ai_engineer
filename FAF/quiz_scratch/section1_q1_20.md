### Question 1
**Difficulty:** Beginner

A Databricks developer wants a language model to return a customer sentiment analysis as a JSON object with the fields `sentiment` and `confidence_score`. What is the most basic first step to achieve this structured output?

A) Deploy a custom fine-tuned model on Databricks Model Serving that has been trained to always output JSON, replacing the need for any prompt-level instructions.
B) Add explicit format instructions to the system prompt, such as "Return ONLY a valid JSON object with keys 'sentiment' and 'confidence_score'. Do not add markdown or prose."
C) Use the `ai_summarize()` SQL function instead of calling the model directly, since summarization functions natively return structured JSON output.
D) Configure the Databricks Model Serving endpoint to automatically convert all plain text responses into JSON format before returning them to the caller.

**Correct Answer:** B
**Explanation:** B is correct because explicitly instructing the model in the system prompt is the fundamental starting point for controlling output format. The model needs to be told what format is expected. A is wrong because fine-tuning a model just for JSON output is expensive and unnecessary when prompt instructions achieve the same result reliably. C is wrong because `ai_summarize()` returns a plain text string, not a structured JSON object, and it is designed for text condensing, not structured extraction. D is wrong because Model Serving endpoints do not have a built-in setting to auto-convert text to JSON; that transformation is the developer's responsibility.
**Source:** Section 1: Design Applications – Objective 1: Design a prompt that elicits a specifically formatted response

---

### Question 2
**Difficulty:** Beginner

A business analyst asks: "Our company needs to automatically pull the invoice number, vendor name, and total amount from thousands of incoming email bodies stored in a Delta table." Which Databricks AI function is the most appropriate for this task?

A) `ai_summarize()` — because it can condense the email text down to the key financial fields that need to be captured in structured form.
B) `ai_classify()` — because it categorizes each email into predefined classes such as 'invoice', 'receipt', or 'other', which identifies the relevant records.
C) `ai_extract()` — because it parses unstructured text and pulls out specific named entities (invoice number, vendor name, total amount) into a structured schema.
D) `ai_translate()` — because vendor names from international suppliers may be in foreign languages and need to be standardized before extraction.

**Correct Answer:** C
**Explanation:** C is correct because `ai_extract()` is specifically designed for information extraction — it takes unstructured text and a target schema, then returns the specified fields as structured output, exactly what is needed here. A is wrong because `ai_summarize()` produces a shorter text summary, not structured key-value fields. B is wrong because `ai_classify()` assigns a category label to the whole document, it does not extract specific data fields from the text. D is wrong because `ai_translate()` converts text between languages; while it may be a useful pre-processing step, it does not extract invoice fields.
**Source:** Section 1: Design Applications – Objective 2: Select model tasks to accomplish a given business requirement

---

### Question 3
**Difficulty:** Beginner

In a standard RAG (Retrieval-Augmented Generation) chain built on Databricks, what is the correct sequential order of components?

A) Prompt Template → Retriever → LLM → Output Parser → User Input, because context must be prepared before the user query is added.
B) User Input → LLM → Retriever → Prompt Template → Output Parser, because the LLM first identifies what to retrieve before the retriever fetches documents.
C) User Input → Retriever → Prompt Template → LLM → Output Parser, because context is first retrieved, then assembled into a prompt, sent to the LLM, and the output is structured.
D) User Input → Output Parser → Prompt Template → Retriever → LLM, because the output format must be defined first before the rest of the chain is assembled.

**Correct Answer:** C
**Explanation:** C is correct. In a RAG chain, the user's query first goes to the Retriever (Databricks Vector Search) to fetch relevant document chunks. Those chunks are then combined with the query in the Prompt Template. The formatted prompt goes to the LLM (a Databricks Model Serving endpoint), and the LLM's text output is finally processed by the Output Parser into the desired structure. A is wrong because the user input is the entry point, not the last step. B is wrong because the LLM does not call the retriever directly; the retriever runs first as a separate, dedicated component. D is wrong because the Output Parser processes the LLM's response at the end, not at the beginning.
**Source:** Section 1: Design Applications – Objective 3: Select chain components for a desired model input and output

---

### Question 4
**Difficulty:** Beginner

A data engineer has built a LangChain RAG application on Databricks and is about to log it with `mlflow.langchain.log_model()`. Their manager asks: "How do we ensure the model serving endpoint validates incoming payloads at runtime?" What does the engineer need to include when logging the model?

A) A `tags` dictionary mapping input field names to their Python types, which MLflow reads at deployment time to enforce basic type checking on the serving endpoint.
B) A `run_name` parameter that describes the expected input format in human-readable text, which Databricks Model Serving parses to build a validation schema.
C) A `signature` object created by `mlflow.models.infer_signature()` or defined manually, which formally specifies the input and output schemas enforced at the serving endpoint.
D) A `pip_requirements` list that includes a schema-validation library such as `pydantic`, which the serving endpoint automatically uses to validate every incoming request.

**Correct Answer:** C
**Explanation:** C is correct because the MLflow Model Signature is the formal mechanism for defining and enforcing the input/output schema. When a model is deployed to Databricks Model Serving, the endpoint reads the logged signature and returns an error for any payload that doesn't match. A is wrong because MLflow `tags` are metadata strings for tracking purposes only; they have no schema enforcement capability at runtime. B is wrong because `run_name` is just a display label for the MLflow experiment run and is not parsed for schema information. D is wrong because `pip_requirements` lists Python packages for the serving environment; installing pydantic does not automatically create any validation at the endpoint level.
**Source:** Section 1: Design Applications – Objective 4: Translate business use case goals into a description of the desired inputs and outputs

---

### Question 5
**Difficulty:** Beginner

A team is building a Databricks chatbot that must answer questions exclusively from the company's private HR policy documents. No public internet data should be used. Which Agent Brick pattern is the most appropriate?

A) Multiagent Supervisor, because it orchestrates multiple specialized sub-agents, one of which can be configured to block access to external internet sources while another handles internal documents.
B) Knowledge Assistant, because it is designed as a RAG-based conversational agent that retrieves answers from a private, internal knowledge base stored in Databricks Vector Search.
C) Information Extraction, because it transforms the HR policy PDFs into structured Delta table rows, which the chatbot can then query using standard SQL without needing an LLM.
D) Function Calling Agent, because it uses Unity Catalog Functions to search HR documents and enforces Unity Catalog access controls, preventing any external data from being accessed.

**Correct Answer:** B
**Explanation:** B is correct. The Knowledge Assistant is the Agent Brick specifically designed for conversational Q&A over private, unstructured data. It uses Vector Search for retrieval and an LLM for generation, grounded entirely in the internal knowledge base. A is wrong because Multiagent Supervisor is designed for cross-domain routing complexity, which is overkill for a single-domain HR chatbot; it doesn't inherently block internet access. C is wrong because Information Extraction is an output pipeline (unstructured → structured data), not a conversational chatbot pattern. D is wrong because "Function Calling Agent" describes the mechanism used within agent patterns, not a standalone Agent Brick template; Unity Catalog governance alone doesn't map to this conversational use case.
**Source:** Section 1: Design Applications – Objective 6: Determine how and when to use Agent Bricks

---

### Question 6
**Difficulty:** Intermediate

A developer's LangChain chain is using `JsonOutputParser` but the model keeps returning responses like: ` ```json\n{"key": "value"}\n``` ` which causes the parser to throw an exception. What is the most targeted fix?

A) Replace `JsonOutputParser` with `StrOutputParser` and then manually call `json.loads()` on the string output in a post-processing step, accepting the added complexity.
B) Switch the model endpoint from `databricks-meta-llama-3-70b-instruct` to a smaller model such as `databricks-dbrx-instruct`, which produces cleaner JSON without markdown wrappers.
C) Add an explicit instruction to the system prompt such as "Return ONLY the raw JSON object. Do not wrap it in markdown code fences or add any other text before or after the JSON."
D) Set the `temperature` parameter to 0.0 on the model call, which forces the model into a deterministic mode that eliminates formatting variations in its output.

**Correct Answer:** C
**Explanation:** C is correct. The model is following a default behavior of wrapping code in markdown fences. Adding an explicit negative instruction ("Do NOT wrap in markdown") directly addresses the root cause without changing the parser or the model. A is wrong because it works around the problem but adds manual parsing code and abandons the structured parser, which is less maintainable. B is wrong because switching models is disruptive and unjustified; the same behavior can occur with any instruction-tuned model and is controlled through prompting. D is wrong because `temperature=0.0` affects randomness in word choice, not formatting behaviors like adding code fences, which are learned tendencies from training.
**Source:** Section 1: Design Applications – Objective 1: Design a prompt that elicits a specifically formatted response

---

### Question 7
**Difficulty:** Intermediate

A content operations team at a media company needs to process a backlog of 50,000 news articles stored in a Delta table. They need to reduce each article to a 3-sentence executive summary. They have no need for real-time processing. Which approach is most appropriate on Databricks?

A) Deploy a real-time streaming pipeline using Spark Structured Streaming that calls a Foundation Model API endpoint for each article as it arrives in the Delta table Change Data Feed.
B) Use the `ai_summarize()` SQL function in a batch Databricks SQL query with a serverless warehouse, processing the full table at once for cost-efficient bulk summarization.
C) Call `ai_extract()` on each article row using a Databricks Workflow job, providing a schema that defines the three required sentences as separate extractable fields.
D) Build a LangChain chain with a `ChatDatabricks` LLM and `StrOutputParser`, then apply it row-by-row using a Spark UDF in a batch notebook scheduled in a Databricks Workflow.

**Correct Answer:** B
**Explanation:** B is correct. `ai_summarize()` is the dedicated Databricks SQL AI function for text condensing/summarization, and running it as a batch SQL query against the full Delta table is the most efficient approach for a bulk, non-real-time workload. A is wrong because real-time streaming adds unnecessary complexity and cost for a backlog-processing use case with no real-time requirement. C is wrong because `ai_extract()` is for information extraction (pulling out specific named entities), not for generating new summarized prose. D is wrong because using a Spark UDF with a LangChain chain works but is significantly more complex and less cost-efficient than the native `ai_summarize()` SQL function for this straightforward summarization task.
**Source:** Section 1: Design Applications – Objective 2: Select model tasks to accomplish a given business requirement

---

### Question 8
**Difficulty:** Intermediate

In a LangChain RAG chain on Databricks, a developer removes the `PromptTemplate` component and directly connects the Retriever output to the LLM. What is the most likely outcome?

A) The chain works correctly because modern LLMs like `databricks-meta-llama-3-70b-instruct` can process raw retrieved document chunks directly without needing a formatted prompt template.
B) The chain throws a type error at runtime because the Retriever returns `Document` objects, while the LLM expects a formatted string or a list of chat messages.
C) The chain produces lower-quality answers because the LLM receives documents but no question, so it summarizes the documents instead of answering a specific user query.
D) The chain automatically falls back to the LLM's built-in knowledge when no prompt template is provided, ignoring the retrieved documents and answering from its training data.

**Correct Answer:** B
**Explanation:** B is correct. The Retriever returns LangChain `Document` objects containing text chunks. The LLM component expects a properly formatted string or `ChatMessage` list. Without the `PromptTemplate` to merge the user question and the retrieved documents into a single formatted string, the chain encounters a type mismatch and fails at runtime. A is wrong because even capable LLMs cannot consume raw `Document` Python objects — the data must be serialized into text within a prompt. C is wrong because the chain would fail with an error before producing any output at all, not silently degrade in quality. D is wrong because LangChain chains do not have an automatic fallback to training data; they execute the defined pipeline and raise errors if the data types are incompatible.
**Source:** Section 1: Design Applications – Objective 3: Select chain components for a desired model input and output

---

### Question 9
**Difficulty:** Intermediate

A developer uses `mlflow.models.infer_signature()` to create an MLflow Model Signature for a RAG chain. They provide a sample `model_input` dictionary `{"query": "What is the return policy?"}` and the corresponding `model_output` string `"Returns are accepted within 30 days."` What does `infer_signature()` produce?

A) A signature object where the input schema specifies a required string field named `query` and the output schema specifies a string type, inferred from the provided sample data.
B) A signature object that captures the full internal architecture of the chain (retriever, LLM, parser) so Databricks Model Serving can reconstruct the pipeline on deployment.
C) A Python dictionary that maps input field names to their Python types, which must be manually converted to an MLflow `ModelSignature` object before being passed to `log_model()`.
D) A validation schema that is stored in the MLflow model artifact and enforces that only queries fewer than 512 tokens are accepted by the serving endpoint.

**Correct Answer:** A
**Explanation:** A is correct. `infer_signature()` inspects the shape and type of the provided sample input and output data to construct a `ModelSignature` object defining the expected input schema (`{query: string}`) and output schema (`string`). It works from sample data, not from the model internals. B is wrong because `infer_signature()` does not inspect or capture the internal architecture of the chain — it only looks at the input/output data shapes. C is wrong because `infer_signature()` directly returns a `ModelSignature` object, not a plain dictionary that needs further conversion. D is wrong because the signature defines data types and field names, not token-length limits; token-length constraints are not part of the MLflow signature specification.
**Source:** Section 1: Design Applications – Objective 4: Translate business use case goals into a description of the desired inputs and outputs

---

### Question 10
**Difficulty:** Intermediate

A Databricks engineer is building an agent that must handle two types of tasks: querying a live sales database and sending Slack notifications. They register both as Unity Catalog Functions. In what order should these tools be presented to the agent, and why?

A) The Slack notification tool should be listed first so that the agent greets the user immediately upon receiving any task request, before querying the database for the actual data.
B) The database query tool should be listed first, as conventions in Databricks' Mosaic AI Agent Framework recommend read-type (knowledge-gathering) tools before write/action tools.
C) The tool order does not matter because the agent's LLM determines which tool to call dynamically at runtime based on the task description, regardless of their order in the tool list.
D) Both tools should be wrapped in a single Unity Catalog Function that the agent calls once, and an internal routing script decides whether to query the database or send a notification.

**Correct Answer:** B
**Explanation:** B is correct. Best practice in multi-stage reasoning is to order knowledge-gathering (read) tools before action (write/side-effect) tools. The agent must first gather the relevant sales data before it can decide whether and what to notify via Slack. Providing the tools in this logical order makes the agent's reasoning flow more predictable and prevents premature actions. A is wrong because sending a Slack greeting before retrieving data provides no useful information to the user and represents an incorrect task order. C is wrong because while the LLM does dynamically decide which tool to call, presenting tools in a logical order (read before write) improves the reliability and predictability of the agent's multi-step reasoning. D is wrong because combining tools into a single function defeats the modular purpose of the agent framework and makes it harder to reuse, test, or update individual capabilities.
**Source:** Section 1: Design Applications – Objective 5: Define and order tools for multi-stage reasoning

---

### Question 11
**Difficulty:** Advanced

A developer has a production LangChain chain where `PydanticOutputParser` is used to enforce a strict output schema. During load testing, 8% of responses cause a `OutputParserException`. Analysis shows the LLM occasionally adds a brief explanation sentence before the JSON. What is the most robust production fix without switching models?

A) Catch the `OutputParserException` in a try/except block and return a default empty Pydantic model instance for failed parses, accepting the data loss in exchange for pipeline stability.
B) Add a `.with_retry()` call to the LLM component in the chain so that any response failing the parser automatically triggers a fresh LLM call with the same prompt, up to 3 times.
C) Add a `.with_structured_output()` method call on the `ChatDatabricks` LLM object with the Pydantic model as the schema, which instructs the model API to enforce structured output natively.
D) Replace `PydanticOutputParser` with `JsonOutputParser` and add a separate Pydantic validation step after the chain, since `JsonOutputParser` is more lenient about surrounding text.

**Correct Answer:** C
**Explanation:** C is correct. The `.with_structured_output()` method, available on `ChatDatabricks` and other LangChain chat models, passes the schema directly to the model's API, instructing it to return only valid structured output without surrounding text. This is far more robust than parser-side fixes because it eliminates the malformed output at the source. A is wrong because silently swallowing parse errors and returning empty models creates silent data corruption in a production pipeline — the lost data is never surfaced. B is wrong because `.with_retry()` is useful for transient errors, but retrying with the same prompt that caused the failure will likely fail again if the model's tendency is to add explanatory text. D is wrong because `JsonOutputParser` also fails when there is surrounding text unless the JSON is clearly delimited; it doesn't fundamentally solve the surrounding-text problem.
**Source:** Section 1: Design Applications – Objective 1: Design a prompt that elicits a specifically formatted response

---

### Question 12
**Difficulty:** Advanced

A company processes legal contracts. They need a pipeline that first classifies each contract by type (NDA, MSA, SOW) and then extracts specific clauses only relevant to that type. They have 200,000 contracts in a Delta table. Which architecture is correct?

A) Use `ai_classify()` in a single SQL query to classify all contracts, then run a second SQL query using `ai_extract()` with conditional logic per type to extract the relevant clauses, storing results in a Delta table.
B) Build one combined LangChain chain that uses a single LLM prompt to simultaneously classify the contract type and extract all possible clauses from all contract types in a single pass.
C) Use `ai_summarize()` on each contract first to reduce its size, then apply `ai_classify()` on the summary, then use `ai_extract()` on the original full text for clause extraction.
D) Use a Multiagent Supervisor where the classifier agent and the extractor agent run in parallel simultaneously on each contract, then a third agent merges their outputs into the final result.

**Correct Answer:** A
**Explanation:** A is correct. This is a two-step task selection pipeline: first use `ai_classify()` to label each contract, then use `ai_extract()` with type-conditional schemas to pull the relevant clauses. This maps each sub-task to the correct AI function and is efficient at scale using Databricks SQL with a serverless warehouse. B is wrong because a single prompt doing both classification and extraction for all contract types simultaneously creates an overly complex prompt, increases token cost, and is less accurate than chaining specialized steps. C is wrong because summarizing before extraction risks losing the exact clause text needed for extraction, and the summarization step adds unnecessary cost and latency. D is wrong because a Multiagent Supervisor is designed for routing between different domains, not for parallel sub-tasks on a single document; this adds orchestration overhead without benefit.
**Source:** Section 1: Design Applications – Objective 2: Select model tasks to accomplish a given business requirement

---

### Question 13
**Difficulty:** Advanced

A developer adds a reranker component between the Retriever and the Prompt Template in a RAG chain. What is the reranker's specific function, and what problem does it solve?

A) The reranker converts the retrieved document chunks from plain text into vector embeddings, allowing the Prompt Template to perform a second round of semantic similarity filtering before assembly.
B) The reranker re-scores the retrieved documents using a cross-encoder model that considers both the query and each document together, reordering them so the most relevant chunks appear first for the LLM.
C) The reranker compresses multiple retrieved documents into a single concatenated string to reduce the total token count sent to the LLM, staying within the context window limit.
D) The reranker applies guardrail filtering to remove any retrieved documents that contain PII or policy-violating content before they are included in the prompt sent to the LLM.

**Correct Answer:** B
**Explanation:** B is correct. A reranker uses a cross-encoder model that jointly encodes the query and each retrieved document to produce a more accurate relevance score than the initial vector similarity search (which uses a bi-encoder). This reordering ensures the most relevant chunks are placed first in the prompt, improving answer quality. A is wrong because the retriever already performed embedding-based search; the reranker works on text chunks already retrieved, using a cross-encoder, not by creating new embeddings. C is wrong because a reranker reorders documents by relevance score; it does not compress or concatenate them. Compression is done by a separate technique called "contextual compression." D is wrong because guardrail filtering is a security/governance concern handled by the Unity AI Gateway or application-layer filters, not by a reranker component.
**Source:** Section 1: Design Applications – Objective 3: Select chain components for a desired model input and output

---

### Question 14
**Difficulty:** Advanced

A team registers a LangChain RAG chain to Unity Catalog using `mlflow.set_registry_uri("databricks-uc")` and `registered_model_name="prod.rag.hr_chatbot"`. The registration fails with: `MlflowException: Model schema validation failed: missing required signature`. What is the root cause and fix?

A) The model name format is incorrect; Unity Catalog requires a two-level namespace (`schema.model`) not a three-level namespace (`catalog.schema.model`), so the name should be changed to `rag.hr_chatbot`.
B) The `mlflow.set_registry_uri("databricks-uc")` call must be made inside the MLflow run context (`with mlflow.start_run():`), otherwise Unity Catalog cannot detect the experiment association.
C) Unity Catalog model registration requires a logged MLflow Model Signature; the team must provide an `input_example` or manually create and pass a `signature` object to `mlflow.langchain.log_model()`.
D) The LangChain model must be converted to a `mlflow.pyfunc` flavor before registering to Unity Catalog, because the `mlflow.langchain` flavor is not supported by the Unity Catalog Model Registry.

**Correct Answer:** C
**Explanation:** C is correct. Unity Catalog's Model Registry mandates that all registered models include an MLflow Model Signature defining the input/output schema. Without it, registration fails. The fix is to provide an `input_example` (so MLflow auto-infers the signature) or to explicitly create a signature using `mlflow.models.infer_signature()` and pass it to `log_model()`. A is wrong because `prod.rag.hr_chatbot` is a valid three-level Unity Catalog namespace (`catalog.schema.model`) which is the correct and required format. B is wrong because `mlflow.set_registry_uri()` is a global configuration call and does not need to be inside the run context; it can be called before the run starts. D is wrong because `mlflow.langchain` is a fully supported MLflow flavor for Unity Catalog registration; there is no requirement to convert to `pyfunc`.
**Source:** Section 1: Design Applications – Objective 4: Translate business use case goals into a description of the desired inputs and outputs

---

### Question 15
**Difficulty:** Advanced

A Mosaic AI Agent uses three Unity Catalog Function tools: `search_product_catalog`, `check_inventory_levels`, and `send_reorder_email`. A user asks: "Do we need to reorder Product X?" How should the agent's reasoning sequence these tool calls, and what governs this sequencing?

A) The agent calls all three tools simultaneously in parallel using Spark parallelism to minimize latency, then consolidates the results to formulate the final answer about reordering.
B) The agent calls `send_reorder_email` first as a precautionary measure, then `check_inventory_levels` to verify, then `search_product_catalog` to confirm the product exists before canceling or confirming.
C) The LLM within the agent dynamically reasons over the task at each step — calling `search_product_catalog` first to find Product X, then `check_inventory_levels` to assess stock, then conditionally calling `send_reorder_email` only if inventory is low.
D) The agent always calls the tools in the order they are listed in the Unity Catalog Function registry, executing `search_product_catalog`, then `check_inventory_levels`, then `send_reorder_email` regardless of the intermediate results.

**Correct Answer:** C
**Explanation:** C is correct. In the Mosaic AI Agent Framework, the LLM acts as the reasoning engine that dynamically decides which tool to call and when, based on the current state of the task. It reads the task, calls the knowledge-gathering tools first (catalog search → inventory check), then conditionally calls the action tool (email) only if the business logic (low inventory) is satisfied. A is wrong because agents in this framework call tools sequentially with reasoning between each call; parallel tool execution is not the default behavior and would not allow the agent to use the result of one tool to inform the next call. B is wrong because sending the email first (before verifying inventory) is the opposite of the correct logical order and would cause false reorder emails. D is wrong because the agent's LLM, not the registry listing order, governs tool call sequencing; the agent reasons dynamically.
**Source:** Section 1: Design Applications – Objective 5: Define and order tools for multi-stage reasoning

---

### Question 16
**Difficulty:** Proficiency

A company's support operations team wants a single AI system that can: (1) answer questions from the internal knowledge base (PDFs, wikis), (2) query the live CRM database to get customer account details, and (3) route complex escalations to a specialized billing agent. An engineer proposes using a single Knowledge Assistant Agent Brick. What is wrong with this proposal?

A) Nothing is wrong; a Knowledge Assistant can be configured with multiple Vector Search indexes for PDFs and wikis, native SQL tool access for CRM queries, and conditional escalation routing in a single agent.
B) The Knowledge Assistant is limited to retrieval from a single Vector Search index and cannot simultaneously serve as a CRM query tool and an escalation router; a Multiagent Supervisor is required.
C) The Knowledge Assistant only supports synchronous request-response interactions and cannot handle the asynchronous escalation routing required for handoffs to the billing agent.
D) Knowledge Assistants are deprecated in the current Mosaic AI Agent Framework and should be replaced with a custom `mlflow.pyfunc` chain that manually implements retrieval, SQL queries, and routing.

**Correct Answer:** B
**Explanation:** B is correct. The Knowledge Assistant Agent Brick is designed specifically for RAG-based Q&A over a private document knowledge base. It does not natively handle cross-system routing (CRM queries + document retrieval + sub-agent escalation). This multi-domain, multi-capability requirement maps to the Multiagent Supervisor pattern: a supervisor LLM routes each request to the appropriate specialized sub-agent (a Document Agent, a CRM Query Agent, and a Billing Escalation Agent). A is wrong because while a Knowledge Assistant can technically be extended, the scenario describes distinct domains requiring routing logic that is architecturally beyond the Knowledge Assistant's design. C is wrong because the limitation is architectural (single retrieval domain), not a synchronous/asynchronous constraint. D is wrong because Knowledge Assistants are not deprecated; they are a current, supported Agent Brick pattern in the Mosaic AI Agent Framework.
**Source:** Section 1: Design Applications – Objective 6: Determine how and when to use Agent Bricks

---

### Question 17
**Difficulty:** Proficiency

A developer logs a RAG chain with `mlflow.langchain.log_model()` and provides an `input_example={"query": "test"}`. Later, the team adds a second input field `session_id` to support multi-turn conversations. They update the code and redeploy. What failure will they encounter and why?

A) The serving endpoint silently ignores the new `session_id` field because MLflow signatures are additive — new fields not in the original signature are accepted but not validated.
B) The serving endpoint rejects all incoming requests that include `session_id` because the logged model signature only specifies `query`, and the endpoint enforces the original signature strictly, returning a schema validation error.
C) MLflow automatically detects the new `session_id` field at serving time by re-running `infer_signature()` against the updated code, updating the signature without requiring a new model log.
D) The serving endpoint accepts requests with `session_id` but strips the field before passing data to the chain, causing the chain to fail with a `KeyError` when it attempts to read `session_id` from the input.

**Correct Answer:** B
**Explanation:** B is correct. The MLflow Model Signature is a schema frozen at `log_model()` time. The serving endpoint enforces this schema strictly — any payload fields not in the signature, or missing required fields, result in a schema validation error. To add `session_id`, the team must re-log the model with a new signature that includes both `query` and `session_id`, then redeploy. A is wrong because MLflow signatures are not permissive about extra fields; the enforcement is strict by design to prevent silent data contract violations. C is wrong because `infer_signature()` is called explicitly by the developer, not automatically by the serving infrastructure at runtime. D is wrong because the validation happens at the endpoint boundary before the request reaches the chain; the request is rejected, not silently modified.
**Source:** Section 1: Design Applications – Objective 4: Translate business use case goals into a description of the desired inputs and outputs

---

### Question 18
**Difficulty:** Proficiency

A developer is deciding between `JsonOutputParser` and `PydanticOutputParser` for a production RAG chain that must return structured data including a `confidence: float` field that must be between 0.0 and 1.0. Which parser is strictly required, and why?

A) `JsonOutputParser` is strictly required because it produces a Python dictionary without additional class overhead, and the `confidence` range validation should be handled downstream by the application consuming the API response.
B) `PydanticOutputParser` is strictly required because it uses a Pydantic model with field validators to enforce type correctness AND value constraints (e.g., `0.0 ≤ confidence ≤ 1.0`) at parse time, catching invalid LLM outputs before they propagate.
C) Either parser is equally suitable because both automatically inject format instructions into the prompt and both validate that numeric fields fall within declared ranges when parsing the LLM response.
D) `StrOutputParser` is strictly required as a first pass to capture the raw LLM response, which must then be validated by a separate Pydantic model before being returned, since neither JSON parser handles range constraints.

**Correct Answer:** B
**Explanation:** B is correct. `PydanticOutputParser` wraps a Pydantic model, which supports field validators (e.g., `@validator` or `Field(ge=0.0, le=1.0)`) that enforce both type correctness and value constraints at parse time. If the LLM returns a `confidence` of `1.5` or `"high"`, the parser raises a validation error immediately. A is wrong because `JsonOutputParser` only checks that the response is valid JSON and produces a raw dictionary — it has no concept of field-level type or range validation. C is wrong because `JsonOutputParser` does NOT validate numeric ranges; this is a key distinction between the two parsers. D is wrong because using `StrOutputParser` plus a separate Pydantic step works but is more complex and gives up the built-in prompt injection and integrated error handling that `PydanticOutputParser` provides.
**Source:** Section 1: Design Applications – Objective 1: Design a prompt that elicits a specifically formatted response

---

### Question 19
**Difficulty:** Proficiency

An enterprise's AI platform team needs to expose a business-specific "classify email urgency" capability to 12 different downstream applications. The classification logic uses the `databricks-meta-llama-3-70b-instruct` model with a highly tuned system prompt and returns a structured JSON. What is the most architecturally sound approach to expose this as a reusable, governed capability?

A) Copy and paste the LangChain chain code, including the system prompt, into each of the 12 downstream applications' notebooks, ensuring each application maintains its own local version of the classification logic.
B) Package the classification chain as an MLflow `pyfunc` model with a defined signature, register it to Unity Catalog, deploy it as a Databricks Model Serving endpoint, and have all 12 applications call the single REST endpoint.
C) Register the classification logic as a Unity Catalog SQL function using `CREATE FUNCTION`, so all 12 downstream applications can call it using `SELECT ai_classify_urgency(email_text) FROM emails`.
D) Store the tuned system prompt in a Databricks Secret scope and have each application fetch the prompt at runtime, construct their own LangChain chain locally, and call the model endpoint directly.

**Correct Answer:** B
**Explanation:** B is correct. Packaging the chain as an MLflow pyfunc model with a signature, registering to Unity Catalog, and deploying as a Model Serving endpoint creates a single, governed, versioned API. All 12 applications consume one endpoint. Changes to the chain logic (prompt updates, model swap) are deployed once without touching any downstream application code. A is wrong because duplicating code across 12 applications creates a maintenance nightmare — any prompt improvement requires 12 simultaneous updates with high risk of divergence. C is wrong because Unity Catalog SQL functions using `CREATE FUNCTION` support user-defined Python/SQL logic but are not the standard mechanism for deploying complex LangChain chains with multi-step reasoning as a shared API. D is wrong because having each application construct its own chain introduces distributed maintenance, inconsistency, and eliminates centralized governance over model versioning.
**Source:** Section 1: Design Applications – Objective 4: Translate business use case goals into a description of the desired inputs and outputs

---

### Question 20
**Difficulty:** Proficiency

During a production incident, a Multiagent Supervisor routes a user query to a SQL Agent sub-agent. The SQL Agent calls a Unity Catalog Function that queries a customer PII table. The query succeeds and PII is included in the final response returned to the end user. The data governance team says this should not be possible. What is the most likely root cause?

A) The Multiagent Supervisor incorrectly routed the query to the SQL Agent instead of the Document Agent, and fixing the routing logic will prevent SQL Agent from being called for this query type.
B) The Unity Catalog Function tool lacks an `EXECUTE` privilege restriction — the agent's service principal has `EXECUTE` on the function AND the underlying table has no column masking or row filter policies applied.
C) The `ChatDatabricks` LLM model used by the Supervisor does not support Unity Catalog access controls, so all tool calls bypass governance regardless of the Unity Catalog permissions configuration.
D) The MLflow Model Signature for the SQL Agent does not specify PII restrictions in its output schema, so the serving endpoint returns all fields including PII without any filtering.

**Correct Answer:** B
**Explanation:** B is correct. Unity Catalog governs access at the identity level — the agent's service principal must have `EXECUTE` on the function AND the underlying table must have column masking or row-level filters to prevent PII from being returned. If the service principal has `EXECUTE` on the function and no masking policies are applied to the PII columns, the query succeeds and returns raw PII. A is wrong because even if routing were corrected, the underlying data governance gap (no masking policies) would still exist — a different query from a different agent could expose the same PII. C is wrong because `ChatDatabricks` fully respects Unity Catalog governance; it operates under the identity of the endpoint creator, who must have appropriate privileges. D is wrong because MLflow Model Signatures define input/output data types and shapes for validation, not data governance or PII filtering; they have no role in Unity Catalog access control.
**Source:** Section 1: Design Applications – Objective 5: Define and order tools for multi-stage reasoning
