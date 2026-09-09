### Question 1
**Difficulty:** Beginner

A data scientist needs to classify 2 million product descriptions stored in a Delta table into one of 5 categories. No real-time response is needed — it is a nightly batch job. Which tool is most appropriate?

A) LangChain with a `ChatDatabricks` LLM and a LangGraph agent that loops through each row and calls a classification tool registered as a Unity Catalog Function for each product description.
B) Databricks `ai_classify()` SQL AI function in a batch SQL query against the Delta table, using a serverless warehouse to process all 2 million rows without needing any LangChain or agent infrastructure.
C) A LangGraph stateful agent with a directed graph that branches between 5 different classification nodes — one per category — and routes each product description to the appropriate node at runtime.
D) A REST call to the Foundation Model API for each row using a Python `for` loop inside a Databricks notebook, which submits each product description individually for classification.

**Correct Answer:** B
**Explanation:** B is correct. For batch inference at scale on structured Delta table data, Databricks SQL AI functions (`ai_classify()`) are the most efficient tool. They run natively in a SQL query on a serverless warehouse, parallelizing across millions of rows without any orchestration code. A is wrong because using LangChain + LangGraph for a simple batch classification task adds enormous unnecessary complexity — LangGraph is designed for stateful, multi-step agents with branching logic, not bulk SQL classification. C is wrong for the same reason — a multi-node directed graph adds orchestration overhead where a single SQL function call is sufficient. D is wrong because a sequential Python `for` loop is the least efficient approach — it processes one row at a time with no parallelism, would take hours or days for 2 million rows, and ignores Databricks' native scalable SQL AI functions.
**Source:** Section 3: Application Development – Objective 1: Select LangChain/similar tools for use in a Generative AI application — docs.databricks.com (search: "Log and deploy LangChain models with MLflow")

---

### Question 2
**Difficulty:** Beginner

During manual review of a deployed RAG chatbot's outputs, an evaluator notices: "The chatbot confidently states that the company's return policy allows 60-day returns, but the retrieved policy document clearly states 30 days." Which LLM failure mode does this represent?

A) Relevance failure — the chatbot returned an answer that is technically on-topic (return policy) but failed to address the user's specific sub-question about the exact number of return days allowed.
B) Verbosity issue — the chatbot's answer is too long and buries the correct 30-day figure under excessive prose, making it appear as if the incorrect 60-day figure was stated prominently.
C) Hallucination — the chatbot generated a confidently stated fact (60-day returns) that contradicts the retrieved context, inventing information not supported by the provided documents.
D) Format issue — the chatbot returned the return policy information in plain prose instead of a structured bullet list, which caused the evaluator to misread the 30 as 60 in the unformatted text.

**Correct Answer:** C
**Explanation:** C is correct. Hallucination occurs when the LLM generates factually incorrect information that contradicts or is not supported by the retrieved context — even when the correct information was provided. The chatbot had the correct 30-day policy in context but generated "60 days," which is a classic hallucination where the model's parametric (training) knowledge or random generation overrides the provided factual context. A is wrong because a relevance failure means the answer is off-topic — this answer IS on-topic (return policy) but contains wrong facts, which is hallucination. B is wrong because verbosity describes excessive length, not factual incorrectness; the problem here is the wrong number, not the answer's length. D is wrong because the problem is not formatting — the chatbot stated an incorrect fact (60 days instead of 30), not a formatting choice that caused visual confusion.
**Source:** Section 3: Application Development – Objective 2: Qualitatively assess responses to identify common issues — docs.databricks.com (search: "Human evaluation Mosaic AI Agent Framework")

---

### Question 3
**Difficulty:** Beginner

After running MLflow evaluation on a RAG pipeline, the team finds `Precision@5 = 0.62` (many irrelevant chunks retrieved). Based on this metric result, which chunking strategy adjustment should they make?

A) Switch to larger chunks (e.g., increase from 256 to 1,024 tokens) so each chunk contains more context, reducing the number of chunks in the index and making the retriever more selective.
B) Switch to smaller, more focused chunks (e.g., reduce from 1,024 to 256 tokens) so that each chunk's embedding is more specific and the retriever returns fewer off-topic results.
C) Add chunk overlap (e.g., 100-token overlap) to the current chunking strategy, which improves precision by ensuring no content is lost at chunk boundaries and reduces the retrieval of irrelevant chunks.
D) Switch from fixed-size chunking to Parent-Child chunking, which retrieves a larger parent block for the LLM while indexing small child chunks — directly addressing the low precision caused by large embeddings.

**Correct Answer:** B
**Explanation:** B is correct. Low `Precision@k` means many of the retrieved chunks are irrelevant — the embeddings are too broad and match too many queries. The fix is to reduce chunk size: smaller chunks produce more focused, specific embeddings that only match queries that are truly relevant to that narrow piece of content. A is wrong because increasing chunk size makes each embedding even broader and less specific — this would further reduce precision, not improve it. C is wrong because chunk overlap prevents context loss at boundaries but does not improve retrieval precision; overlap affects recall (not missing split content) rather than precision (not returning irrelevant content). D is wrong because Parent-Child chunking is designed to address low LLM answer quality after accurate retrieval — its primary mechanism (small child embeddings for search precision) is relevant here, but the guidance for low precision without context issues is simply to reduce chunk size.
**Source:** Section 3: Application Development – Objective 3: Select chunking strategy based on model & retrieval evaluation — docs.databricks.com (search: "RAG evaluation chunking Databricks")

---

### Question 4
**Difficulty:** Beginner

A user asks a banking chatbot: "What are my loan options as a small business owner?" The developer wants the LLM to produce a more targeted answer by detecting the user's customer segment. Which prompt augmentation approach is correct?

A) Extract `customer_segment = "small business owner"` from the user's query and inject it as a named variable into the `PromptTemplate` system message, so the LLM is told upfront the user's context before generating an answer.
B) Pass the raw user query directly to the LLM without modification and rely on the LLM's training data to infer that "small business owner" implies a specific set of loan products, since modern LLMs handle this implicitly.
C) Replace the user's full query with only the extracted key term `"small business owner"` before passing it to the retriever, discarding the original query to make the retrieval more precise.
D) Store `customer_segment = "small business owner"` as a Databricks Secret and have the LLM read the secret at inference time to personalize its response without the segment appearing in the visible prompt.

**Correct Answer:** A
**Explanation:** A is correct. Prompt augmentation means extracting key signals from the user input (here: `customer_segment = "small business owner"`) and injecting them as structured context into the prompt template before the LLM call. A LangChain `ChatPromptTemplate` with named variables like `{customer_segment}` and `{retrieved_documents}` assembles a rich, targeted prompt that produces a more relevant answer than the raw query alone. B is wrong because relying on the LLM's implicit inference from raw queries misses the opportunity to explicitly steer the response — injecting structured context is reliably more accurate than hoping the LLM infers correctly. C is wrong because replacing the full query with just a key term discards the user's actual question — the retriever needs the full query to find relevant loan documents; the extracted term is supplemental context, not a replacement. D is wrong because Databricks Secrets store credentials (API keys, passwords), not dynamic user context; injecting user context through secrets is architecturally incorrect and would not provide per-query personalization.
**Source:** Section 3: Application Development – Objective 4: Augment a prompt with additional context from a user's input — docs.databricks.com (search: "PromptTemplate LangChain MLflow Databricks")

---

### Question 5
**Difficulty:** Beginner

A developer's RAG chatbot is returning correct information but the LLM is responding in French when users ask in English. The developer wants to enforce English-only responses. What is the most direct fix?

A) Add a language detection step after the LLM response using `langdetect` Python library, and if a non-English response is detected, retry the LLM call with a higher temperature to force English output.
B) Add a strict instruction to the system message in the prompt template: "Always respond in English only, regardless of the language of the user's question or retrieved documents."
C) Replace the current LLM endpoint with an English-only fine-tuned model deployed on Databricks Provisioned Throughput, which is architecturally guaranteed to never generate non-English responses.
D) Enable the Databricks Unity AI Gateway language filter, which automatically detects and translates all LLM outputs to English before they are returned to the calling application.

**Correct Answer:** B
**Explanation:** B is correct. Adding a clear behavioral constraint to the system message ("Always respond in English only") is the most direct, lowest-cost prompt engineering fix. System role instructions are the standard mechanism for enforcing behavioral constraints like language, tone, and format in LLM applications. A is wrong because using a post-generation language detector with retry is fragile — higher temperature makes output more random, not more English; retry-based fixes add latency and don't address the root cause. C is wrong because fine-tuning a model is an expensive, time-consuming solution for what is a trivially fixable prompt engineering problem; no "English-only" fine-tuned model guarantees zero non-English output anyway. D is wrong because Unity AI Gateway does not include an automatic language translation filter — guardrails address safety, PII, and jailbreak detection, not language enforcement.
**Source:** Section 3: Application Development – Objective 5: Create a prompt that adjusts an LLM's response from a baseline to a desired output — docs.databricks.com (search: "Prompt engineering Databricks Foundation Model APIs")

---

### Question 6
**Difficulty:** Intermediate

A company deploys a customer support chatbot. Management requires that the chatbot must never reveal internal product pricing discussions or mention competitor product names. These are company-specific policies not covered by standard safety filters. What is the correct Databricks implementation?

A) Add instructions to the system prompt like "Never mention competitor names or internal pricing" — this is sufficient since system prompt instructions are enforced as hard constraints by all Databricks Foundation Model API models.
B) Enable the built-in Unity AI Gateway safety guardrail toggle, which includes pre-configured rules for blocking competitor mentions and internal business terminology as part of its standard content moderation policy.
C) Write a custom SQL function defining the organization-specific blocking rules and attach it to the Unity AI Gateway serving endpoint as an ON CALL (input) and/or ON RESULT (output) policy to enforce the rules technically.
D) Route all chatbot traffic through a separate Databricks Workflow job that post-processes each LLM response with a regex filter, blocking any response containing competitor names before it is returned to the user.

**Correct Answer:** C
**Explanation:** C is correct. Custom organization-specific policies (blocking competitor names, confidential terminology) are implemented as custom SQL functions attached to the Unity AI Gateway endpoint. An `ON CALL` policy inspects and filters the user's input before it reaches the LLM; an `ON RESULT` policy inspects and filters the LLM's output before it reaches the user. This is a hard technical enforcement mechanism that cannot be bypassed through prompt manipulation. A is wrong because system prompt instructions are a soft guardrail — a determined user can often override them through prompt injection; they are not a technical enforcement mechanism. B is wrong because Unity AI Gateway's built-in safety guardrails cover generic categories (hate speech, violence, sexual content, PII) — they do not include company-specific policies like blocking competitor names. D is wrong because routing through a separate Workflow job for post-processing adds significant latency and operational complexity; the Unity AI Gateway ON RESULT policy achieves the same thing natively at the endpoint level.
**Source:** Section 3: Application Development – Objective 6: Implement LLM guardrails to prevent negative outcomes — docs.databricks.com (search: "Configure guardrails Unity AI Gateway")

---

### Question 7
**Difficulty:** Intermediate

A team is building a real-time customer support chat interface. Response time is critical — responses must arrive within 1 second. They are evaluating `databricks-meta-llama-3-70b-instruct` vs. `databricks-meta-llama-3-8b-instruct`. Which model should they choose and why?

A) Choose `llama-3-70b-instruct` because it has a larger context window (128K tokens) which guarantees faster token generation per second compared to the 8B model's smaller context window.
B) Choose `llama-3-8b-instruct` because smaller models generate tokens significantly faster with lower latency — the 8B model's speed makes it suitable for real-time chat where response time is the primary constraint.
C) Choose `llama-3-70b-instruct` because pay-per-token pricing for the 70B model is cheaper than the 8B model, meaning the team can afford faster infrastructure that reduces latency below 1 second.
D) Choose `llama-3-8b-instruct` only if the application needs to process more than 10 concurrent users; for fewer than 10 users, both models have identical latency characteristics on Databricks Foundation Model APIs.

**Correct Answer:** B
**Explanation:** B is correct. Model size directly correlates with latency — smaller models (8B parameters) generate tokens much faster than larger models (70B parameters) because they have fewer computations per forward pass. For a real-time chat interface with a 1-second response SLA, the 8B model's lower latency is the primary selection criterion. The 70B model is reserved for tasks requiring higher reasoning quality where latency is less critical (batch processing, complex analysis). A is wrong because context window size does not determine token generation speed — the 70B model's 128K context window is not faster than the 8B model; in fact, larger models are slower. C is wrong because pay-per-token pricing is based on token count, not model size in a way that relates to infrastructure speed; you cannot "buy faster infrastructure" through pricing tier selection on pay-per-token. D is wrong because latency characteristics between model sizes exist regardless of concurrent user count; a 70B model is slower per request than an 8B model at any concurrency level.
**Source:** Section 3: Application Development – Objective 7: Select the best LLM based on attributes of the application — docs.databricks.com (search: "Supported models Foundation Model APIs")

---

### Question 8
**Difficulty:** Intermediate

A developer is setting up a RAG pipeline for a legal document knowledge base. The source documents are dense 100-page legal briefs. Relevant information often spans multiple consecutive paragraphs. The embedding model being considered has a maximum context of 512 tokens. Is 512 tokens sufficient, or should they choose a longer-context embedding model?

A) 512 tokens is sufficient because legal briefs can always be meaningfully chunked at sentence boundaries, and sentence-level embeddings capture all necessary semantic information for legal retrieval tasks.
B) 512 tokens may be insufficient if key legal arguments span more than ~380 words. For long narrative documents where context spans multiple paragraphs, a longer-context embedding model (8,192 tokens) or Parent-Child chunking with a 512-token model should be considered.
C) 512 tokens is always sufficient because the retriever does not need to understand multi-paragraph context — it only needs to match keywords between the query and individual chunk tokens, making context length irrelevant.
D) 512 tokens is more than sufficient because Databricks Vector Search automatically summarizes each chunk before embedding, so the effective semantic content of any chunk always fits within 512 tokens regardless of original document length.

**Correct Answer:** B
**Explanation:** B is correct. 512 tokens (~380 words) is adequate for dense factual Q&A, but legal briefs where arguments span multiple paragraphs create a tradeoff: smaller chunks (to fit 512 tokens) lose inter-paragraph context, while larger chunks get truncated. The correct decision depends on the retrieval evaluation results — if retrieval is accurate but LLM answers lack context, use a longer-context model (8K tokens) or apply Parent-Child chunking (small child for precise retrieval, large parent for rich LLM context). A is wrong because legal arguments are NOT always expressible at sentence level — complex reasoning spanning paragraphs gets fragmented by sentence-boundary splitting, losing critical logical connections. C is wrong because modern embedding models use semantic similarity (dense vector matching), not keyword matching (BM25); context length determines how much semantic content the model can encode in one vector. D is wrong because Databricks Vector Search does not automatically summarize chunks — it embeds the raw chunk text as-is; summarization is a separate pre-processing step the developer must explicitly implement.
**Source:** Section 3: Application Development – Objective 8: Select an embedding model context length — docs.databricks.com (search: "Embedding models Foundation Model APIs")

---

### Question 9
**Difficulty:** Intermediate

A developer discovers a model called `MedLlama-3-8B` in the Databricks Marketplace. Before using it for a clinical documentation assistant at a hospital, what information from the model card is MOST critical to verify?

A) The model's inference speed benchmark (tokens per second) on an A100 GPU, which determines whether it can meet the hospital's 500ms response time SLA during peak usage hours.
B) The model's intended use case, training data (was it trained on medical text?), known limitations/biases relevant to clinical use, and license terms (does it allow commercial healthcare use?).
C) The model's MMLU benchmark score, which measures general knowledge across 57 subjects and is the definitive indicator of a model's suitability for medical documentation tasks.
D) The model's maximum context window length, which determines the longest patient note it can process in a single inference call without chunking or truncation.

**Correct Answer:** B
**Explanation:** B is correct. For a healthcare application, the model card's most critical sections are: (1) **Intended use** — is this model designed for clinical tasks or general text? (2) **Training data** — was it trained on medical literature (PubMed, clinical notes) or general web text? (3) **Known limitations/biases** — does it hallucinate drug dosages or mishandle rare conditions? (4) **License** — does the license permit commercial use in a healthcare setting? Missing any of these could result in clinical errors or legal violations. A is wrong because inference speed, while important for SLA planning, is not the most critical safety concern for a clinical application — using a medically inaccurate model quickly is worse than using an accurate model slightly more slowly. C is wrong because MMLU measures general academic knowledge across 57 subjects — while informative, it is not a clinical benchmarking standard; clinical-specific benchmarks (MedQA, MedMCQA) would be more relevant. D is wrong because context window length is an operational concern for long documents, not a safety or suitability concern; the most critical issue for a hospital application is medical accuracy and compliance, not context length.
**Source:** Section 3: Application Development – Objective 9: Select a model from a model hub based on model metadata/model cards — docs.databricks.com (search: "Databricks Marketplace models")

---

### Question 10
**Difficulty:** Intermediate

A team runs MLflow experiments comparing three LLMs for a legal document summarization task. Results: Model A: `groundedness=0.91`, `latency_ms=2800`, `cost_per_1k=0.18`. Model B: `groundedness=0.88`, `latency_ms=950`, `cost_per_1k=0.06`. Model C: `groundedness=0.73`, `latency_ms=400`, `cost_per_1k=0.02`. The use case is a nightly batch summarization job — quality is the top priority, cost is secondary, and latency is irrelevant. Which model should be selected?

A) Model C because it has the lowest cost and latency, and for a nightly batch job these are the most important operational metrics since the job runs while users are asleep.
B) Model B because it offers the best balance — nearly as good groundedness as Model A (0.88 vs 0.91) at one-third the cost and one-third the latency, making it the most practical production choice.
C) Model A because it achieves the highest groundedness score (0.91), and since the use case explicitly states quality is the top priority and latency is irrelevant for a nightly batch job, the best quality model is the correct choice.
D) Model B because its latency of 950ms meets the real-time SLA of under 1 second that most legal document applications require, whereas Model A's 2800ms latency would violate the SLA.

**Correct Answer:** C
**Explanation:** C is correct. The evaluation criteria are explicit: quality (groundedness) is the top priority, cost is secondary, and latency is irrelevant (it's a batch job). Model A has the highest groundedness (0.91) — it is the objectively best-quality model for the stated requirements. The 3× higher cost over Model B is acceptable given the explicit secondary-priority status of cost, especially for a legal domain where summarization errors have serious consequences. A is wrong because cost and latency are explicitly the lowest priorities; choosing the cheapest/fastest model (C) when quality matters most produces legally unreliable summaries. B is wrong because while Model B offers a compelling cost-quality tradeoff, the team explicitly stated quality is the TOP priority — and Model A outperforms Model B on groundedness by a meaningful margin (0.91 vs 0.88) in a high-stakes legal context. D is wrong because the scenario explicitly states latency is irrelevant for a nightly batch job — there is no "real-time SLA of under 1 second" in this use case.
**Source:** Section 3: Application Development – Objective 10: Select the best model based on common metrics generated in experiments — docs.databricks.com (search: "MLflow evaluate generative AI")

---

### Question 11
**Difficulty:** Advanced

A developer calls `mlflow.langchain.autolog()` before running their LangChain RAG chain. What is automatically captured, and how does it differ from manually calling `mlflow.log_metric()`?

A) `autolog()` captures only the final LLM response and logs it as a single MLflow artifact; `mlflow.log_metric()` captures intermediate step metrics — so the two approaches are complementary and both must be called together.
B) `autolog()` automatically captures the full execution trace — every LLM call, tool invocation, retrieved document, prompt sent, and response received — as a structured MLflow Trace with timing, without any manual logging code. `mlflow.log_metric()` only logs a single scalar value you explicitly specify, requiring manual code for each metric.
C) `autolog()` captures aggregate experiment-level statistics (total token count, average latency) and writes them to the MLflow tracking server; `mlflow.log_metric()` captures per-step execution details within a single chain run.
D) `autolog()` and `mlflow.log_metric()` capture identical information — the difference is that `autolog()` uses asynchronous background logging that doesn't block chain execution, while `log_metric()` logs synchronously and may increase latency.

**Correct Answer:** B
**Explanation:** B is correct. `mlflow.langchain.autolog()` hooks into LangChain's callback system to automatically capture every execution detail as a structured MLflow Trace: each LLM call (prompt in, response out), tool invocations with their inputs/outputs, retrieved documents, intermediate chain steps, and timing for each span — all without any manual logging code. `mlflow.log_metric()` is a single explicit call that logs one scalar value (e.g., `mlflow.log_metric("latency", 450)`) — you must call it manually for every metric you want to capture. A is wrong because `autolog()` captures far more than just the final response — it captures every intermediate step; and the two are not always complementary — `autolog()` often makes manual `log_metric()` calls redundant. C is wrong because `autolog()` captures per-run step-level details (the trace), not aggregate statistics; aggregate statistics would be computed separately from trace data. D is wrong because both `autolog()` and `log_metric()` can operate asynchronously or synchronously; the fundamental difference is the scope of what they capture (full trace vs. single scalar), not their threading model.
**Source:** Section 3: Application Development – Objective 11: Utilize MLflow and Agent Framework for developing agentic systems — docs.databricks.com (search: "mlflow.langchain autolog tracing")

---

### Question 12
**Difficulty:** Advanced

A production RAG agent has been deployed for 3 months. The ML team wants to know: "Has the agent's answer quality degraded since launch?" Which Databricks component provides this answer, and what data does it use?

A) The MLflow Experiment UI — it compares the pre-deployment evaluation run (the baseline) against new development runs logged by engineers during the same 3-month period, detecting any performance regression introduced by code changes.
B) Databricks Inference Tables combined with Agent Monitoring — Inference Tables log all live production inputs and outputs; Agent Monitoring periodically evaluates a sample of production traffic against quality scorers, tracking metrics like groundedness and relevance over time.
C) The MLflow Review App — it displays all production responses to the agent's developer team, who manually review each response daily and report quality trends through a weekly stakeholder dashboard.
D) Databricks Lakehouse Monitoring applied to the model serving endpoint's system metrics table, which tracks infrastructure metrics like CPU utilization and memory usage to infer when the model's hardware environment degrades answer quality.

**Correct Answer:** B
**Explanation:** B is correct. Monitoring post-deployment quality drift requires: (1) Inference Tables to capture all live production traffic (inputs and outputs), and (2) Agent Monitoring to periodically score sampled production responses against quality metrics (groundedness, relevance, safety) and alert when scores drop below thresholds. This answers "Is the agent still performing well after we shipped it?" A is wrong because the MLflow Experiment UI compares pre-deployment development runs, not post-deployment production traffic; it answers "Is this agent good enough to ship?" not "Is it still performing after shipping?" C is wrong because manually reviewing every production response is operationally infeasible at scale and does not provide automated trend detection — this is a qualitative development-phase activity, not a scalable monitoring approach. D is wrong because CPU utilization and memory usage are infrastructure metrics that indicate compute health — they do not measure answer quality (groundedness, relevance) and cannot detect semantic quality degradation.
**Source:** Section 3: Application Development – Objective 12: Compare evaluation and monitoring phases — docs.databricks.com (search: "Mosaic AI Agent Monitoring" and "Inference tables Databricks Model Serving")

---

### Question 13
**Difficulty:** Advanced

A Multiagent Supervisor receives the query: "What were our top 5 products by revenue last quarter, and summarize why they performed well?" The supervisor routes this to a Genie Agent. How does the Genie Agent process this request?

A) The Genie Agent sends the full natural language query to the foundation LLM which directly queries the Unity Catalog Delta tables via JDBC, and returns the query results alongside a natural language explanation.
B) The Genie Agent accepts the natural language question, generates and executes the appropriate SQL query against registered Unity Catalog tables to fetch the top 5 products by revenue, and returns the structured data result to the supervisor for further processing.
C) The Genie Agent converts the natural language query into a vector search against a pre-built revenue knowledge base, retrieves the top 5 product summary documents, and returns them as text chunks to the supervisor.
D) The Genie Agent uses the MCP protocol to broadcast the query to all registered Genie Spaces simultaneously and returns the first result it receives, making it non-deterministic which Unity Catalog table is queried.

**Correct Answer:** B
**Explanation:** B is correct. Genie Agents (formerly Genie Spaces) are Databricks-native natural language interfaces for structured data. They accept a user's natural language question, use an LLM to generate the appropriate SQL query, execute it against the registered Unity Catalog tables, and return the structured result (the top 5 products by revenue). The supervisor can then pass this structured data result to a separate summarization LLM to generate the "why they performed well" explanation. A is wrong because LLMs do not have native JDBC connectivity — the Genie Agent is an intermediary that generates and executes SQL; the LLM alone cannot directly query Delta tables. C is wrong because Genie Agents work with structured tabular data via SQL — not vector search over document knowledge bases; vector search is for unstructured document retrieval. D is wrong because the Genie Agent queries a specific, configured Genie Space tied to designated Unity Catalog tables — it does not broadcast to all registered Genie Spaces simultaneously; routing is deterministic.
**Source:** Section 3: Application Development – Objective 13: Enable multi-agent systems to leverage Genie Agents — docs.databricks.com (search: "Genie Agents API Databricks")

---

### Question 14
**Difficulty:** Advanced

A developer builds a stateful customer support agent that must: (1) gather the user's account information, (2) check their order history, (3) conditionally route to either a refund processing node or a technical support node based on the complaint type, and (4) generate a final response. Which framework best supports this multi-step, branching workflow?

A) A simple LangChain `LLMChain` with a linear sequence of steps — since it supports prompt templates and LLM calls in sequence, adding conditional logic via Python `if/else` after each chain step handles the routing.
B) A direct Foundation Model API call with a complex multi-thousand-token prompt that encodes all four steps and the branching logic in the system message, relying on the LLM to self-direct through all steps.
C) LangGraph — it models the agent as a directed graph where each step (gather info, check history, route, generate response) is a node, and edges define the conditional routing logic (refund node vs. technical support node) between nodes.
D) Databricks SQL AI functions (`ai_query()`) — they support multi-step processing with native SQL CASE statements for conditional routing between refund and technical support categories.

**Correct Answer:** C
**Explanation:** C is correct. LangGraph is designed exactly for stateful, multi-step agents with conditional branching. Each processing step becomes a graph node (gather account info, check order history, refund processing, technical support), and edges define the routing conditions (if complaint_type == 'billing' → refund node, else → technical support node). LangGraph maintains state between nodes and supports complex decision trees that linear chains cannot express cleanly. A is wrong because a linear `LLMChain` does not natively support stateful branching — while you can add Python `if/else` after each step, this is brittle, hard to maintain, and loses the state management, replay, and observability benefits that LangGraph provides. B is wrong because encoding all four steps and conditional logic in a single massive system prompt leads to unreliable behavior — the LLM may skip steps, misinterpret conditions, or lose state across reasoning steps without a structured graph to enforce the workflow. D is wrong because Databricks SQL AI functions are for batch data processing, not interactive stateful agent workflows; SQL CASE statements cannot maintain conversational state across multiple LLM reasoning steps.
**Source:** Section 3: Application Development – Objective 1 & 11: Select LangChain/similar tools and utilize MLflow/Agent Framework — docs.databricks.com (search: "LangGraph agents on Databricks")

---

### Question 15
**Difficulty:** Advanced

A team uses `mlflow.evaluate()` to compare two RAG chain versions before production deployment. Run A: `groundedness=0.82`, `answer_relevance=0.79`. Run B: `groundedness=0.88`, `answer_relevance=0.71`. The application is a compliance document assistant where factual accuracy (groundedness) is paramount, but users also report that relevance matters. How should the team select the model?

A) Select Run A because `answer_relevance=0.79` is higher and user-perceived relevance directly determines customer satisfaction, which is the primary commercial KPI for a compliance assistant.
B) Select Run B because `groundedness=0.88` significantly outperforms Run A on the most critical metric for a compliance application — answers must be factually supported by documents. The relevance gap (0.79 vs 0.71) should be investigated to determine if relevance can be improved via prompt engineering without sacrificing groundedness.
C) Average the two metrics for each run: Run A = 0.805, Run B = 0.795. Select Run A because it has the higher average score, indicating overall superiority across both dimensions equally weighted.
D) Neither run is acceptable until both metrics reach 0.90 simultaneously — compliance applications require perfect scores on all quality dimensions before any production deployment is permitted.

**Correct Answer:** B
**Explanation:** B is correct. For a compliance document assistant, groundedness (factual support from documents) is the paramount metric — a non-grounded answer in a compliance context could cite regulations incorrectly or fabricate requirements, with serious legal consequences. Run B's groundedness of 0.88 significantly outperforms Run A's 0.82. The relevance gap (0.71 vs 0.79) is meaningful but can potentially be addressed through prompt engineering — adjusting the prompt to make the LLM produce more on-topic responses — without necessarily sacrificing groundedness. A is wrong because choosing the model with better relevance when groundedness is explicitly the top priority for compliance use cases prioritizes the wrong metric; a highly relevant but poorly grounded answer is dangerous in compliance. C is wrong because simple averaging treats both metrics as equally important, ignoring the explicit requirement that groundedness is paramount — weighted scoring based on business priorities should govern model selection. D is wrong because requiring 0.90 on all metrics simultaneously before deployment is an arbitrary threshold that may never be achievable; production deployment decisions should be based on business risk tolerance and whether the metrics are "good enough" given the use case, not theoretical perfection.
**Source:** Section 3: Application Development – Objective 10: Select the best model based on common metrics — docs.databricks.com (search: "MLflow evaluate generative AI" and "MLflow experiment tracking comparison")

---

### Question 16
**Difficulty:** Proficiency

A developer uses few-shot prompting with 5 examples in the system message to improve JSON format compliance. The compliance rate improves from 68% to 93% but average latency increases from 350ms to 1,100ms. The application must process 50,000 requests/day with a 500ms P95 latency SLA. The team cannot change the model. What is the most architecturally sound resolution?

A) Reduce the number of few-shot examples from 5 to 2, accepting a reduction in format compliance (estimated ~83%) in exchange for reduced latency, then use a post-processing `json.loads()` with error handling to recover from the remaining ~17% format failures.
B) Keep all 5 few-shot examples and deploy the endpoint behind a Unity AI Gateway rate limiter set to 500 requests/minute, which throttles the incoming traffic to prevent SLA violations from concurrent high-load periods.
C) Replace few-shot prompting with `.with_structured_output()` on the `ChatDatabricks` model — it passes the schema to the model's native structured output API, achieving near-100% format compliance at near-zero additional token cost, eliminating the latency overhead from few-shot examples.
D) Move the few-shot examples from the system message to a Databricks Volume file and load them at application startup, which caches the examples in memory and reduces the per-request token encoding time to under 100ms.

**Correct Answer:** C
**Explanation:** C is correct. `.with_structured_output()` passes the output schema directly to the model's API as a structured output parameter (function-calling / JSON mode), instructing the model to generate only valid structured JSON. This achieves near-100% compliance without adding any few-shot example tokens to the prompt — eliminating the 750ms latency overhead caused by the 5 examples. The latency returns to near the original 350ms baseline while maintaining or improving compliance. A is wrong because reducing to 2 examples is a compromise that accepts lower compliance and requires brittle error handling — better alternatives exist and the team should not accept degraded compliance when `.with_structured_output()` is available. B is wrong because rate limiting at 500 req/min reduces throughput (500 × 60 × 24 = 720,000 potential slots — adequate for volume), but it doesn't fix the P95 latency problem; each individual request still takes 1,100ms, violating the 500ms SLA. D is wrong because loading few-shot examples from a file at startup is already the standard pattern — the latency overhead comes from the token count of the examples being encoded per request, not from file I/O at startup; caching them in memory doesn't reduce the per-request token cost.
**Source:** Section 3: Application Development – Objective 5: Create a prompt that adjusts an LLM's response — docs.databricks.com (search: "Prompt engineering Databricks Foundation Model APIs")

---

### Question 17
**Difficulty:** Proficiency

A healthcare company must comply with HIPAA when deploying an LLM application. A compliance officer asks: "Does using Databricks pay-per-token Foundation Model APIs satisfy our HIPAA requirement that PHI (Protected Health Information) must not leave our cloud environment?" How should the engineer respond?

A) Yes — pay-per-token endpoints are fully HIPAA-compliant because all Databricks Foundation Model APIs run exclusively on Databricks-managed infrastructure within the customer's AWS/Azure/GCP cloud region, ensuring PHI stays within the cloud boundary.
B) No — pay-per-token Foundation Model APIs use shared serverless infrastructure managed by Databricks; PHI sent through these endpoints may traverse Databricks-managed infrastructure outside the customer's dedicated environment. Provisioned Throughput endpoints on dedicated compute should be used for HIPAA workloads.
C) Yes — HIPAA compliance is automatically satisfied by enabling the Unity AI Gateway PII redaction guardrail before sending data to pay-per-token endpoints, which strips all PHI from requests so no protected information ever reaches the model.
D) No — HIPAA requirements cannot be satisfied using any Databricks Foundation Model API regardless of endpoint type; all clinical AI applications must be deployed on on-premises hardware to ensure PHI never leaves the physical facility.

**Correct Answer:** B
**Explanation:** B is correct. Pay-per-token Foundation Model APIs use shared, serverless multi-tenant infrastructure managed by Databricks — PHI sent through these endpoints traverses infrastructure that is not dedicated to the customer's environment. For HIPAA compliance, which requires that PHI stays within the customer's controlled, dedicated cloud environment (covered by a Business Associate Agreement), Provisioned Throughput endpoints are the correct choice. Provisioned Throughput deploys the model on dedicated compute within the customer's cloud environment (AWS/Azure/GCP), ensuring PHI does not leave the customer-controlled boundary. A is wrong because pay-per-token endpoints use shared serverless infrastructure — they do not guarantee that requests are processed exclusively on hardware within the customer's dedicated cloud account. C is wrong because Unity AI Gateway PII redaction is a guardrail for general privacy best practices, not a HIPAA compliance mechanism — redacting fields before sending still means PHI traversed non-dedicated infrastructure, and the redaction itself must happen on compliant infrastructure. D is wrong because Provisioned Throughput on Databricks can satisfy HIPAA requirements with an appropriate Business Associate Agreement (BAA) — on-premises deployment is not the only compliant option.
**Source:** Section 3: Application Development – Objective 7: Select the best LLM based on attributes of the application — docs.databricks.com (search: "Provisioned throughput Databricks")

---

### Question 18
**Difficulty:** Proficiency

An agent is deployed using the Mosaic AI Agent Framework. After 6 weeks, the team decides to update the underlying LLM from `databricks-meta-llama-3-70b-instruct` to a newer model. They update the code and re-log the agent with `mlflow.langchain.log_model()`, registering a new version in Unity Catalog. What must they do to make the production endpoint serve the new model version, and what is the zero-downtime approach?

A) The production serving endpoint automatically detects new Unity Catalog model versions and switches to the latest version within 5 minutes without any manual intervention, providing automatic zero-downtime updates.
B) Update the serving endpoint configuration to point to the new model version using the Databricks Model Serving UI or REST API (update `served_models` with the new `model_version`). Use the endpoint's traffic splitting feature to gradually route a percentage of traffic to the new version while keeping the old version live, achieving a canary/blue-green deployment.
C) Delete the existing serving endpoint and create a new one pointing to the new model version; then update the calling application's endpoint URL to the new endpoint address, accepting a brief downtime window during the switchover.
D) Re-register the updated agent under the same Unity Catalog model name and version number (overwriting the existing version), which automatically triggers a hot-reload of the serving endpoint without any traffic interruption.

**Correct Answer:** B
**Explanation:** B is correct. Databricks Model Serving supports traffic splitting between multiple model versions on the same endpoint. The zero-downtime approach is: (1) register the new model version in Unity Catalog, (2) update the endpoint to add the new version as a served model with a small traffic percentage (e.g., 10%), (3) monitor quality metrics for the new version, (4) gradually increase traffic to the new version while decreasing the old version, (5) once satisfied, route 100% to the new version. The old version remains live throughout, ensuring zero downtime. A is wrong because Databricks Model Serving does NOT automatically switch to new Unity Catalog versions — model version management is explicit; auto-updating a production endpoint without review would be unsafe. C is wrong because deleting and recreating the endpoint is the least sophisticated approach — it requires downtime and a URL change in all calling applications. D is wrong because Unity Catalog model versions are immutable once registered — you cannot overwrite an existing version number; each registration creates a new version. Overwriting would also bypass the review process.
**Source:** Section 3: Application Development – Objective 11: Utilize MLflow and Agent Framework for developing agentic systems — docs.databricks.com (search: "Mosaic AI Agent Framework tutorial")

---

### Question 19
**Difficulty:** Proficiency

A company has a multi-agent system where a Supervisor routes queries to a Genie Agent for data retrieval. A data analyst asks: "Show me the revenue trend for Product A over the last 12 months and predict next quarter's revenue." The Supervisor sends this to the Genie Agent. What is the Genie Agent's limitation here, and how should the system handle it?

A) The Genie Agent cannot process queries involving product names — it only handles aggregate metrics like total revenue or average order value. The Supervisor should rephrase the query to remove "Product A" before routing to the Genie Agent.
B) The Genie Agent handles the historical revenue retrieval (SQL query against Unity Catalog tables) but cannot perform forecasting/prediction — the Supervisor should route the retrieved historical data to a separate forecasting model or LLM for the predictive component.
C) The Genie Agent can handle both parts of the query: it retrieves historical revenue via SQL and generates the forecast using built-in time-series forecasting functions available in all Genie Spaces by default.
D) The Genie Agent converts the full query including "predict next quarter's revenue" into a single SQL query using Databricks' native `FORECAST()` SQL function, and returns both historical data and the forecast in one result set.

**Correct Answer:** B
**Explanation:** B is correct. Genie Agents are specialized for natural language → SQL → structured data retrieval. They can handle "Show me revenue for Product A over the last 12 months" by generating and executing a SQL query against Unity Catalog. However, "predict next quarter's revenue" is a forecasting task that requires either a statistical model, an ML model, or an LLM's reasoning capabilities — Genie Agents do not perform predictions. The Supervisor's role is to decompose this compound query: route the historical retrieval to the Genie Agent, then pass the returned data to a forecasting model or an LLM for the prediction component. A is wrong because Genie Agents are fully capable of filtering by product name — `WHERE product_name = 'Product A'` is a basic SQL filter that Genie handles well. C is wrong because Genie Agents do not have built-in time-series forecasting — they are SQL query generators, not ML forecasting tools. D is wrong because while Databricks SQL has a `FORECAST()` function in some contexts (via Prophet integration), Genie Agents do not automatically use it for all prediction queries — and even if available, it would need to be explicitly configured, not assumed as a default behavior.
**Source:** Section 3: Application Development – Objective 13: Enable multi-agent systems to leverage Genie Agents — docs.databricks.com (search: "Genie Agents API Databricks" and "Genie Spaces conversational API")

---

### Question 20
**Difficulty:** Proficiency

An engineer argues: "We should run MLflow evaluation during development AND set up Inference Tables monitoring after deployment — this is redundant and doubles our cost." A senior engineer disagrees. What is the correct technical justification for running both?

A) The senior engineer is wrong — MLflow evaluation and Inference Table monitoring are fully redundant for identical reasons: both use the same LLM judges on the same data types, so one can be safely eliminated to reduce costs without losing any quality signal.
B) The senior engineer is correct — evaluation and monitoring serve fundamentally different purposes: evaluation (pre-deployment) validates the agent on curated benchmark data to determine if it's ready to ship; monitoring (post-deployment) tracks quality on REAL production traffic over time to detect drift, new failure modes, and changing user behavior that no benchmark can anticipate.
C) The senior engineer is partially correct — evaluation is optional if monitoring is implemented, since production monitoring can retroactively identify all quality issues before they cause significant user harm, making pre-deployment evaluation an unnecessary cost.
D) The senior engineer is correct but for the wrong reason — the real justification is that MLflow evaluation is billed per evaluation call while Inference Tables are free, so running both maximizes the value of already-paid infrastructure.

**Correct Answer:** B
**Explanation:** B is correct. Evaluation and monitoring are complementary, non-redundant phases serving different purposes: **Evaluation** (pre-deployment) answers "Is this agent good enough to ship?" — it uses curated benchmark datasets with known correct answers to systematically validate the agent under controlled conditions. **Monitoring** (post-deployment) answers "Is this agent still performing well after we shipped it?" — it operates on real, unpredictable production traffic that no benchmark can fully anticipate, detecting quality drift caused by new user behaviors, evolving knowledge base, model updates, or distribution shift. A is wrong because evaluation and monitoring are NOT redundant — they use different data (benchmark vs. production), different timing (pre vs. post deployment), and answer different questions; eliminating either creates a blind spot. C is wrong because retroactive monitoring cannot prevent harm that occurs between the model going live and the monitoring detecting a problem — pre-deployment evaluation prevents shipping a broken agent in the first place. D is wrong because the justification for running both is the fundamentally different purpose each serves (as described in B), not billing mechanics; Inference Tables do have costs related to storage and querying.
**Source:** Section 3: Application Development – Objective 12: Compare evaluation and monitoring phases — docs.databricks.com (search: "Mosaic AI Agent Monitoring" and "Inference tables Databricks Model Serving")
