### Question 1
**Difficulty:** Beginner

A developer is ingesting plain-text product documentation into a Databricks RAG pipeline. The embedding model they chose has a maximum context limit of 512 tokens. Which chunking concern is MOST critical to address first?

A) The chunks must all contain exactly the same number of sentences so that the LLM receives uniformly structured context regardless of the length of each sentence in the original document.
B) No chunk should exceed 512 tokens, because text beyond the token limit is silently truncated by the embedding model, causing information loss and degrading the quality of the resulting vector.
C) Every chunk must begin with the document's title so the LLM always knows which source document a chunk belongs to, preventing it from confusing content from different product manuals.
D) Each chunk must be stored as a separate file in a Databricks Volume before embedding, because the embedding model cannot process chunks passed as in-memory Python strings directly.

**Correct Answer:** B
**Explanation:** B is correct. Embedding models have a hard token limit; any text beyond that limit is truncated before the embedding is computed. This means part of the chunk's meaning is permanently lost, producing a misleading embedding vector. Ensuring no chunk exceeds 512 tokens is the most fundamental constraint when working with this model. A is wrong because uniform sentence count is not a requirement — chunk quality is about semantic completeness within the token limit, not uniform length. C is wrong because while adding metadata (like document title) is a useful best practice, it is a secondary concern to first ensuring chunks fit the model's token limit. D is wrong because embedding models accept text strings directly in API calls; writing each chunk to a file first is unnecessary overhead with no benefit.
**Source:** Section 2: Data Preparation – Objective 1: Apply a chunking strategy for a given document structure and model constraints — docs.databricks.com (search: "Data preparation for RAG applications")

---

### Question 2
**Difficulty:** Beginner

A data engineer is preparing HTML web pages for a RAG knowledge base. Each page contains the actual article text, but also a navigation bar, header logo text, footer with copyright notices, and cookie consent banners. What should be done to these extra elements before chunking?

A) Include all HTML elements in the chunks unchanged, because the embedding model and LLM are trained on web data and can automatically distinguish navigation text from article content.
B) Replace the navigation, footer, and banner text with placeholder tokens like `[NAV]`, `[FOOTER]`, and `[BANNER]` so the LLM knows to ignore them when generating answers.
C) Filter and remove the navigation bar, header, footer, and cookie banners before chunking, so that only the meaningful article content is embedded and stored in the Vector Search index.
D) Convert all HTML pages to PDF format first, because PDF parsers automatically strip navigation elements and return only the main body text for downstream chunking and embedding.

**Correct Answer:** C
**Explanation:** C is correct. Navigation bars, footers, and cookie banners are extraneous content — they add noise to the embedding without contributing relevant knowledge. Embedding these elements dilutes the semantic signal of the chunk and can cause the retriever to return irrelevant chunks that happen to match boilerplate phrases. Filtering them out using a library like `beautifulsoup4` before chunking is the standard approach. A is wrong because LLMs and embedding models do not automatically filter out boilerplate HTML structure; they treat all ingested text as meaningful content, and repeated boilerplate degrades retrieval quality. B is wrong because placeholder tokens still consume embedding space and teach the retriever to associate queries with boilerplate metadata, which is counterproductive. D is wrong because PDF conversion does not automatically remove navigation elements; HTML-to-PDF tools typically include all visible page elements, and the conversion adds processing overhead without solving the filtering problem.
**Source:** Section 2: Data Preparation – Objective 2: Filter extraneous content in source documents — docs.databricks.com (search: "Generative AI data preparation")

---

### Question 3
**Difficulty:** Beginner

A team has a folder of scanned paper documents (image-based PDFs where the text is not selectable) and needs to extract the text content for a RAG pipeline. Which Python library should they use for this task?

A) `beautifulsoup4` — because it can parse any binary file format including image-based PDFs by treating the file as an HTML document and stripping non-text elements.
B) `PyPDF2` — because it reads PDF files page by page and extracts embedded text, including text in rasterized image layers within the PDF file.
C) `pytesseract` — because it performs Optical Character Recognition (OCR) on images and scanned documents, converting the visual text in the scanned pages into machine-readable strings.
D) `unstructured` — because it natively handles all file formats including scanned image PDFs by directly reading the binary pixel data and converting it to structured text elements.

**Correct Answer:** C
**Explanation:** C is correct. `pytesseract` is Python's wrapper for Google's Tesseract OCR engine. It processes images and scanned PDFs by analyzing the pixel patterns of characters and converting them into text strings. This is the only option that can extract text from image-based content where no digital text layer exists. A is wrong because `beautifulsoup4` is exclusively for parsing HTML/XML structured text — it has no capability to process binary image data or perform OCR. B is wrong because `PyPDF2` can only extract digitally embedded text layers from PDFs — it cannot read text from rasterized image layers (scanned pages), where no text layer exists. D is wrong because while `unstructured` is a powerful multi-format library, it relies on OCR tools (including Tesseract) as a backend for scanned PDFs; `pytesseract` is the direct tool that actually performs the OCR operation.
**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package to extract document content — docs.databricks.com (search: "RAG reference architecture data preparation")

---

### Question 4
**Difficulty:** Beginner

After chunking product documents, a developer has a Spark DataFrame with columns `id` (unique chunk identifier) and `chunk_text` (the text content). What is the correct sequence of operations to prepare this data for Databricks Vector Search?

A) Create the Vector Search index first, then write the DataFrame to a Delta table, then enable Change Data Feed (CDF) on the table so that future updates sync to the index automatically.
B) Write the DataFrame to a Unity Catalog Delta table, enable Change Data Feed (CDF) on the table with `SET TBLPROPERTIES (delta.enableChangeDataFeed = true)`, then create the Vector Search index pointing to that table.
C) Enable CDF on the Unity Catalog schema first, then write the DataFrame to a Delta table, then create a Vector Search endpoint, and finally create the index using the endpoint name as the table reference.
D) Write the DataFrame to a Databricks Volume as JSON files, enable Change Data Feed on the volume folder, then create a Vector Search index pointing to the volume path as the data source.

**Correct Answer:** B
**Explanation:** B is correct. The required sequence is: (1) write chunked data to a Unity Catalog Delta table, (2) enable Change Data Feed on that table (required for Vector Search to detect and sync incremental updates), (3) create the Vector Search index pointing to the Delta table. CDF must be enabled before the index is created so Vector Search can establish the sync pipeline. A is wrong because the index cannot be created before the source table exists and has CDF enabled — Vector Search needs to read the existing table data and set up CDF-based sync at index creation time. C is wrong because CDF is a table-level property, not a schema-level setting; you enable it per-table, not per-schema. D is wrong because Databricks Vector Search requires a Delta Lake table as its source — it does not support Volume JSON files as a sync source, and Volumes do not have Change Data Feed.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Create a Mosaic AI Vector Search index" and "Enable Change Data Feed")

---

### Question 5
**Difficulty:** Beginner

A company is building an IT Support chatbot on Databricks. They have three potential document sources: (A) current approved troubleshooting guides (updated quarterly), (B) legacy system manuals from 2008 that cover deprecated hardware, and (C) employee birthday party announcements from the internal newsletter. Which documents should be included in the RAG knowledge base?

A) All three sources should be included to maximize the breadth of the knowledge base; the LLM will automatically determine which content is relevant and ignore the irrelevant sources at query time.
B) Only source A (current troubleshooting guides) should be included, as it is the only source containing accurate, current, task-relevant information that the chatbot is expected to answer questions about.
C) Sources A and B should be included because the legacy manuals may still contain relevant troubleshooting principles even if the specific hardware is deprecated, giving the chatbot more context depth.
D) Sources A and C should be included because current guides answer technical questions, and newsletter announcements help the chatbot maintain a friendly conversational tone in its responses.

**Correct Answer:** B
**Explanation:** B is correct. The knowledge base should contain only documents that are accurate, current, and directly relevant to the chatbot's purpose (IT support). The 2008 legacy manuals (B) contain outdated information about deprecated hardware that will produce incorrect or misleading answers. The birthday announcements (C) are entirely unrelated and will degrade retrieval precision by matching queries about people's names or dates. Including only source A ensures the highest quality knowledge base. A is wrong because LLMs cannot reliably "ignore" irrelevant retrieved content — they tend to incorporate whatever context they receive, including outdated or irrelevant information, into their generated answers. C is wrong because including deprecated hardware manuals is likely to cause the chatbot to give outdated troubleshooting steps for hardware the company no longer uses. D is wrong because newsletter announcements contain no IT support knowledge; including them would cause the retriever to return birthday announcements as context for technical queries.
**Source:** Section 2: Data Preparation – Objective 5: Identify needed source documents — docs.databricks.com (search: "Generative AI data preparation best practices")

---

### Question 6
**Difficulty:** Intermediate

A developer has chunked a Markdown-formatted technical reference guide using fixed-size chunking with 500 characters and 50-character overlap. Users report that answers about configuration options are incomplete. Analysis shows that configuration tables in the Markdown are being split mid-row across chunk boundaries. What is the most targeted fix?

A) Increase the chunk size from 500 to 5,000 characters, which ensures that even the longest configuration tables fit within a single chunk and are never split across boundaries.
B) Switch from fixed-size chunking to document-aware (structure-based) chunking using Markdown headers and table boundaries as split points, keeping configuration tables intact within a single chunk.
C) Add a 200-character overlap instead of 50 characters so that when a table is split, the overlapping content on both sides reconstructs the missing rows for the LLM during retrieval.
D) Convert the Markdown tables to plain prose before chunking (e.g., "Option X has value Y") so that the fixed-size chunker can split the flattened text without breaking logical table rows.

**Correct Answer:** B
**Explanation:** B is correct. The root cause is that fixed-size chunking is structure-agnostic — it splits by character count regardless of document structure, breaking tables mid-row. Document-aware chunking uses the document's own structure (Markdown headers `##`, horizontal rules, table boundaries) as natural split points. A library like LangChain's `MarkdownHeaderTextSplitter` or `unstructured` can detect these boundaries and keep tables intact within a chunk. A is wrong because increasing chunk size to 5,000 characters is a blunt fix that may solve the immediate problem but creates very large chunks that exceed embedding model token limits and reduce retrieval precision. C is wrong because overlap preserves context at the edge of chunks, but does not reconstruct full table rows; a 200-character overlap would duplicate the row header but not the missing data rows. D is wrong because converting tables to prose is a complex transformation that may lose the relational structure of the table data, making it harder for the LLM to reason about comparative configuration values.
**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies — docs.databricks.com (search: "Advanced chunking strategies RAG")

---

### Question 7
**Difficulty:** Intermediate

After deploying a RAG application on Databricks, a developer wants to measure whether the Vector Search retriever is returning the correct document chunks for a given set of test queries. They have a test dataset with queries and the known correct chunk IDs that should be retrieved. Which approach uses the correct Databricks tooling?

A) Manually compare the retrieved chunk IDs to the expected IDs in a Python loop, calculate a match percentage, and log the result as a custom MLflow metric using `mlflow.log_metric("retrieval_accuracy", score)`.
B) Decorate the retrieval function with `@mlflow.trace(span_type="RETRIEVER")`, then run `mlflow.genai.evaluate()` with the `RetrievalRelevance` scorer, which uses the captured trace data to evaluate retrieval quality.
C) Use Databricks Model Serving's built-in A/B testing framework to compare two retriever configurations and let the platform automatically select the one with higher user click-through rate on retrieved results.
D) Query the Vector Search index directly using the REST API, collect the returned chunk IDs into a Delta table, and then run a Spark JOIN against the expected results table to calculate Precision@k.

**Correct Answer:** B
**Explanation:** B is correct. The Databricks-recommended approach for evaluating retrieval is to instrument the retriever with `@mlflow.trace(span_type="RETRIEVER")` so MLflow captures exactly which chunks were retrieved for each query. Then `mlflow.genai.evaluate()` with the `RetrievalRelevance` scorer uses an LLM judge to assess whether the retrieved chunks are relevant to the query. This integrates seamlessly with MLflow's evaluation framework. A is wrong because manually logging a custom match percentage works but is not the Databricks-recommended approach — it bypasses MLflow's built-in GenAI evaluation framework and provides a less insightful metric than `RetrievalRelevance`. C is wrong because A/B testing with click-through rate is a user behavioral metric, not a retrieval quality metric — it requires actual users, not a test dataset, and measures user engagement, not chunk relevance. D is wrong because manually running a Spark JOIN to calculate Precision@k works as a data engineering approach but bypasses the MLflow evaluation framework and requires significant custom code compared to the native `mlflow.genai.evaluate()` approach.
**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance — docs.databricks.com (search: "MLflow evaluate for RAG" and "MLflow Tracing")

---

### Question 8
**Difficulty:** Intermediate

A RAG application retrieves the top-5 chunks (`k=5`) from Vector Search for each query. A developer wants to understand what `Recall@5` measures in this context and how to interpret a value of 0.6.

A) `Recall@5` measures what fraction of the 5 retrieved chunks are relevant (relevant retrieved ÷ total retrieved), so 0.6 means 3 out of 5 retrieved chunks are relevant to the query.
B) `Recall@5` measures what fraction of ALL known relevant chunks were found in the top-5 results (relevant retrieved ÷ total relevant), so 0.6 means 60% of all relevant chunks exist in the top-5 results.
C) `Recall@5` measures the average rank position of the first relevant chunk within the top-5 results, so 0.6 means the first relevant chunk appears at rank position 3 on a normalized 0-to-1 scale.
D) `Recall@5` measures the semantic similarity score of the 5th-ranked chunk to the query, so 0.6 means the least-relevant chunk in the top-5 has a cosine similarity of 0.6 to the query vector.

**Correct Answer:** B
**Explanation:** B is correct. Recall@k = (number of relevant chunks retrieved in top-k) ÷ (total number of relevant chunks in the dataset). A Recall@5 of 0.6 means that out of all the chunks that are actually relevant to the query (say, 5 relevant chunks exist total), 60% of them (3 chunks) appear in the top-5 retrieved results. High recall means you're not missing relevant information. A is wrong because that definition describes Precision@k, not Recall@k. Precision@5 = (relevant retrieved) ÷ k (total retrieved = 5). C is wrong because that describes Mean Reciprocal Rank (MRR), which measures the rank position of the first relevant result. D is wrong because that describes a raw similarity threshold, not a retrieval recall metric; Recall@k is about coverage of relevant documents, not individual similarity scores.
**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance — docs.databricks.com (search: "MLflow evaluate for RAG")

---

### Question 9
**Difficulty:** Intermediate

A developer needs to extract text from Word documents (`.docx`), HTML web pages, and regular text-based PDFs in a single unified pipeline on Databricks. They want a single Python library that handles all three formats and returns structured output (separating titles from body text). Which library is most appropriate?

A) `PyPDF2` — because it supports cross-format parsing and automatically detects the file type from the file extension, switching between PDF, HTML, and Word parsing modes internally.
B) `pytesseract` — because it uses the underlying image rendering of all document types (converting each format to an image first) to extract text uniformly across PDFs, HTML, and Word documents.
C) `unstructured` — because it is a multi-format document parsing library that handles PDFs, Word, HTML, and many other formats, returning structured elements (titles, narrative text, tables) from each format.
D) `beautifulsoup4` — because it is format-agnostic and can parse the raw binary content of any file type, automatically recognizing Word, HTML, and PDF document structures.

**Correct Answer:** C
**Explanation:** C is correct. `unstructured` is the go-to library for multi-format document ingestion in RAG pipelines. It natively supports `.docx`, `.html`, `.pdf`, and many other formats, and parses them into typed elements (e.g., `Title`, `NarrativeText`, `Table`) — making it ideal for pipelines that need both format flexibility and structured output. A is wrong because `PyPDF2` only handles PDF files; it has no capability to parse Word or HTML documents. B is wrong because `pytesseract` is an OCR library for image-based text; standard Word, HTML, and digital PDFs have embedded text layers that do not need OCR, and pytesseract would be unnecessarily slow and lossy for these formats. D is wrong because `beautifulsoup4` is exclusively an HTML/XML parser; it cannot parse Word documents or PDFs, and it does not process binary file formats.
**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package to extract document content — docs.databricks.com (search: "RAG reference architecture data preparation")

---

### Question 10
**Difficulty:** Intermediate

A Databricks Vector Search index is configured with `pipeline_type="TRIGGERED"` and source table `main.docs.policy_chunks`. A developer updates 500 rows in the source Delta table. When will these updates appear in the Vector Search index?

A) Immediately — because Delta Lake's ACID transactions ensure that all Vector Search indexes always reflect the current committed state of the source table in real time.
B) Within 5 seconds — because `TRIGGERED` mode uses Change Data Feed micro-batching with a default polling interval of 5 seconds to detect and apply changes from the source Delta table.
C) Only after a manual sync is triggered — either by calling `index.sync()` via the Python SDK or scheduling a sync via the Databricks Vector Search UI or REST API, since `TRIGGERED` mode does not auto-sync.
D) At the next scheduled Vector Search maintenance window — because Databricks performs index synchronization during off-peak hours to avoid impacting production query performance.

**Correct Answer:** C
**Explanation:** C is correct. `TRIGGERED` pipeline mode means the Vector Search index only updates when explicitly triggered by calling `index.sync()` (Python SDK), the REST API, or via the UI. Updates to the source Delta table are detected via Change Data Feed, but they do not automatically propagate to the index — the developer must invoke a sync. This mode is suitable for batch workloads where real-time updates are not needed. A is wrong because Delta ACID transactions guarantee consistency at the Delta table level, not at the Vector Search index level; the index is a separate derived artifact that must be explicitly synchronized. B is wrong because micro-batch auto-polling is the behavior of `CONTINUOUS` pipeline mode, not `TRIGGERED` mode; these two modes have fundamentally different sync behaviors. D is wrong because there is no automatic maintenance window sync in Databricks Vector Search; all syncs in `TRIGGERED` mode are explicitly initiated by the developer.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Create a Mosaic AI Vector Search index")

---

### Question 11
**Difficulty:** Advanced

A developer applies fixed-size chunking with 512 tokens and 64-token overlap to a lengthy legal contract. They observe that the embeddings for consecutive chunks have very high cosine similarity (≥ 0.97), making it hard for the retriever to distinguish between adjacent chunks. What is the most likely root cause and the correct fix?

A) The cosine similarity is high because the 64-token overlap introduces duplicate content in consecutive chunks; reducing the overlap to zero eliminates the shared content and creates more distinct embeddings.
B) The cosine similarity is high because legal contracts use highly repetitive boilerplate language (e.g., "the party of the first part shall…"); document-aware chunking by contract section boundaries will produce more semantically distinct chunks.
C) The cosine similarity is high because the embedding model has not been fine-tuned on legal text; replacing the embedding model with a legal-domain-specific model will produce embeddings that better distinguish contract clauses.
D) The cosine similarity is high because 512 tokens is too small for legal text; increasing the chunk size to 2,048 tokens makes each chunk more contextually complete, reducing semantic overlap with neighboring chunks.

**Correct Answer:** B
**Explanation:** B is correct. Legal contracts are densely repetitive — the same boilerplate phrases, party names, and legal constructions appear throughout. Fixed-size chunking cuts across this repeated structure arbitrarily, producing chunks that are semantically nearly identical because they share the same vocabulary and clause patterns. Document-aware chunking by contract section (e.g., "Section 4: Indemnification" as one chunk, "Section 5: Limitation of Liability" as another) produces semantically distinct chunks that are more differentiable. A is wrong because reducing overlap to zero reduces the duplicate content between adjacent chunks but does not solve the root cause — boilerplate legal language across all sections still produces high similarity regardless of overlap size. C is wrong because while a legal-domain embedding model may perform better overall, the root cause here is the structural repetitiveness of the source document, not the embedding model's domain knowledge. D is wrong because larger chunks include more context but the boilerplate density remains; you'd still get high similarity between large chunks filled with similar legal language.
**Source:** Section 2: Data Preparation – Objective 1 & 7: Chunking strategy and advanced chunking — docs.databricks.com (search: "Advanced chunking strategies RAG")

---

### Question 12
**Difficulty:** Advanced

A developer implements Parent-Child chunking for a RAG pipeline. Small "child" chunks (150 tokens) are embedded and stored in Vector Search. When a query matches a child chunk, the retriever fetches the corresponding "parent" chunk (1,000 tokens) to send to the LLM. What problem does this architecture solve compared to embedding large chunks directly?

A) It reduces the total storage cost of the Vector Search index because only the small child embeddings are stored as vectors, while the large parent chunks remain as plain text in the Delta table without requiring vector storage.
B) It solves the precision-context tradeoff: small child chunks produce precise, focused embeddings that match queries accurately (high precision retrieval), while the large parent chunks provide the LLM with sufficient surrounding context to generate a complete answer.
C) It eliminates the need for Change Data Feed because parent chunks are static and never updated — only the child chunks require CDF-based synchronization with the Vector Search index.
D) It improves retrieval speed because the Vector Search index only needs to store a fraction of the data (child chunks), reducing index size and making approximate nearest neighbor search significantly faster.

**Correct Answer:** B
**Explanation:** B is correct. This is the exact problem Parent-Child chunking is designed to solve. Embedding large chunks directly produces "fuzzy" embeddings that mix many topics, making precise query matching harder. Small child chunks produce highly focused, precise embeddings that match specific query terms well. However, when the LLM receives only a 150-token child chunk as context, it often lacks enough surrounding information to generate a complete, well-grounded answer. Fetching the 1,000-token parent chunk gives the LLM rich context while maintaining high retrieval precision. A is wrong because while it is true that only child embeddings are vectorized, the primary motivation for Parent-Child chunking is retrieval precision and context richness, not storage cost reduction. C is wrong because CDF is required whenever the source Delta table is updated, regardless of whether parent or child chunks change — the sync requirement is determined by the table, not by chunk hierarchy. D is wrong because while a smaller index does improve search speed, this is a secondary benefit; the primary architectural motivation is the precision-context tradeoff described in B.
**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies — docs.databricks.com (search: "Advanced chunking strategies RAG")

---

### Question 13
**Difficulty:** Advanced

A developer uses `mlflow.genai.evaluate()` with a `RetrievalRelevance` scorer on a test dataset. The test queries are logged but the scorer returns all null scores. Investigation reveals the `@mlflow.trace(span_type="RETRIEVER")` decorator was not applied to the retrieval function. Why does this cause null scores, and what is the fix?

A) Without the `RETRIEVER` span, MLflow's `RetrievalRelevance` scorer cannot identify which part of the trace corresponds to the retrieval step; it needs the typed span to know which inputs and outputs to pass to the LLM judge for scoring.
B) Without the `RETRIEVER` span, the retrieval function runs synchronously instead of asynchronously, which causes a thread lock that prevents MLflow from recording any evaluation scores during the evaluation run.
C) Without the `RETRIEVER` span, the evaluation function falls back to using the final LLM output instead of the retrieved chunks for scoring, which inflates the relevance scores to 1.0 rather than returning null.
D) Without the `RETRIEVER` span, MLflow cannot authenticate the retrieval function's calls to the Vector Search index, causing a permissions error that silently returns null scores instead of raising an exception.

**Correct Answer:** A
**Explanation:** A is correct. MLflow's `RetrievalRelevance` scorer is specifically designed to evaluate the output of the retrieval step — the documents that were fetched. It finds this data by looking for a trace span typed as `"RETRIEVER"`, which contains the query input and the retrieved documents as outputs. Without this typed span, MLflow cannot locate the retrieval step in the trace tree and has no data to pass to the LLM judge, resulting in null scores. The fix is to add `@mlflow.trace(span_type="RETRIEVER")` to the retrieval function. B is wrong because the `RETRIEVER` span type is metadata for MLflow's evaluation framework — it has no effect on whether the function runs synchronously or asynchronously. C is wrong because without a RETRIEVER span, MLflow doesn't fall back to using LLM output; it simply cannot find the data it needs and produces nulls. D is wrong because MLflow tracing and Vector Search authentication are independent; the `RETRIEVER` decorator is an instrumentation call, not an authentication mechanism.
**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance — docs.databricks.com (search: "MLflow Tracing")

---

### Question 14
**Difficulty:** Advanced

A developer needs to enable Change Data Feed on a Delta table that already has 2 million existing rows before creating a Vector Search index. They run: `ALTER TABLE main.docs.chunks SET TBLPROPERTIES (delta.enableChangeDataFeed = true)`. Will the existing 2 million rows be synced to the Vector Search index when it is created?

A) No — enabling CDF only captures future changes (inserts, updates, deletes) after the property is set. When the Vector Search index is created, it performs an initial full-table snapshot read of all existing rows to seed the index, then uses CDF for subsequent incremental updates.
B) No — enabling CDF on an existing table has no effect on historical data; the Vector Search index will only contain rows that were inserted or updated AFTER CDF was enabled, leaving all 2 million existing rows out of the index.
C) Yes — enabling CDF retroactively creates change records for all 2 million existing rows, which the Vector Search index reads during its first sync to populate the index with all historical data.
D) Yes — but only if the developer runs `OPTIMIZE TABLE main.docs.chunks` after enabling CDF, which compacts the existing data files and triggers CDF to generate historical change records for all rows.

**Correct Answer:** A
**Explanation:** A is correct. When a Vector Search index is created on a Delta table with CDF enabled, it performs an initial full-table snapshot read to seed the index with all existing rows. After this initial load, it uses CDF records to track only incremental changes (new inserts, updates, deletes) going forward. This means all 2 million existing rows are correctly included in the index. B is wrong because it confuses CDF's ongoing behavior (capturing changes) with the index creation behavior (initial full snapshot). The initial snapshot reads all rows regardless of when CDF was enabled. C is wrong because enabling CDF does not retroactively create CDF records for historical data — CDF records only begin from the transaction version when CDF is enabled. The existing rows are captured via the initial snapshot, not via CDF records. D is wrong because `OPTIMIZE` is for file compaction and does not generate CDF records for historical data; it is unrelated to the Vector Search index creation process.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Enable Change Data Feed" and "Create a Mosaic AI Vector Search index")

---

### Question 15
**Difficulty:** Advanced

A developer is building a RAG pipeline for a company that publishes new product release notes weekly. The existing Vector Search index uses `pipeline_type="TRIGGERED"` sync. The team wants to ensure the index reflects new release notes within 1 hour of publication to the Delta table. What is the most operationally efficient solution?

A) Switch the Vector Search index sync pipeline to `CONTINUOUS` mode, which automatically propagates Delta table changes to the index in near-real-time without requiring any scheduled jobs or manual intervention.
B) Keep the `TRIGGERED` mode but deploy a Databricks Workflow job scheduled every 1 hour that calls `index.sync()` on the Vector Search index after new data is written to the source Delta table.
C) Switch to `CONTINUOUS` mode and enable Delta Structured Streaming on the source table, which creates a push-based pipeline where new rows are streamed directly to the Vector Search index as they are committed.
D) Keep `TRIGGERED` mode and configure a Databricks Alert on the source Delta table that sends an API call to `index.sync()` whenever new rows are detected, replacing the need for a scheduled job.

**Correct Answer:** B
**Explanation:** B is correct. For a 1-hour freshness SLA, a scheduled Workflow job that calls `index.sync()` every hour is the most straightforward and operationally efficient solution with `TRIGGERED` mode. This approach is cost-effective (sync only runs when scheduled, not continuously) and meets the SLA. A is wrong because `CONTINUOUS` mode would also satisfy the SLA but is more expensive — it keeps the sync pipeline running continuously even when there are no changes, incurring ongoing compute cost for what is a weekly update pattern. C is wrong because `CONTINUOUS` mode uses CDF-based propagation internally — there is no separate "Delta Structured Streaming push" mechanism for Vector Search; the description conflates two different Databricks technologies. D is wrong because Databricks Alerts are monitoring notifications (email, Slack) triggered by SQL query conditions — they cannot directly call the `index.sync()` API; this would require a webhook integration, which is significantly more complex than a scheduled Workflow job.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Create a Mosaic AI Vector Search index")

---

### Question 16
**Difficulty:** Proficiency

A company ingests 10,000 long-form research papers (each averaging 8,000 tokens) into a RAG pipeline using fixed-size chunking with 512-token chunks and 50-token overlap. Retrieval quality (`Recall@5 = 0.41`) is low. An engineer proposes Parent-Child chunking as the fix. A second engineer argues that improving the embedding model is the right solution. How should the team evaluate which fix addresses the root cause?

A) Run an ablation study: first replace the embedding model while keeping fixed-size chunking, then switch to Parent-Child chunking while keeping the original embedding model, and compare `Recall@5` for each change to determine which variable drives the improvement.
B) Switch to Parent-Child chunking immediately because chunking strategy always has a larger impact on retrieval quality than embedding model selection for long-form documents, making further evaluation unnecessary.
C) Replace the embedding model first because embedding quality is always the primary bottleneck in RAG pipelines; chunking strategy is a secondary factor that only matters after the optimal embedding model is selected.
D) Add more documents to the knowledge base to increase the probability that the correct chunk is retrieved, since low `Recall@5` always indicates a knowledge gap in the source documents rather than a retrieval architecture problem.

**Correct Answer:** A
**Explanation:** A is correct. The correct engineering approach is an ablation study — isolating each variable (embedding model vs. chunking strategy) while holding the other constant, and measuring the impact on `Recall@5`. This produces evidence about which factor is the actual bottleneck. For 8,000-token papers with 512-token chunks, both factors could be significant: large papers may have relevant content spread across many chunks (favoring Parent-Child), and a weak embedding model may fail to match query semantics (favoring model upgrade). B is wrong because there is no universal rule that chunking always dominates over embedding quality — the relative importance depends on the specific content type, query patterns, and current setup; assuming so without evidence is a logical error. C is wrong for the same reason as B but in the opposite direction — there is no universal hierarchy that embedding model always matters more than chunking. D is wrong because `Recall@5 = 0.41` means 41% of known relevant chunks are found in top-5 — the relevant content is in the index (otherwise recall would be 0); the problem is the retrieval system's ability to surface it, not a gap in the knowledge base.
**Source:** Section 2: Data Preparation – Objective 6 & 7: Evaluate retrieval and advanced chunking — docs.databricks.com (search: "MLflow evaluate for RAG" and "Advanced chunking strategies RAG")

---

### Question 17
**Difficulty:** Proficiency

A re-ranking stage is added after Vector Search retrieval in a RAG pipeline. Vector Search returns the top-50 candidate chunks; the reranker scores all 50 and passes the top-5 to the LLM. A senior engineer says: "If the correct chunk isn't in the top-50 from Vector Search, the reranker cannot help." Is this statement accurate, and what design implication does it have?

A) The statement is inaccurate — rerankers can retrieve additional chunks from the Vector Search index beyond the initial top-50 candidates if they detect that the top-50 set does not contain a high-confidence match.
B) The statement is accurate — the reranker only scores candidates already retrieved by Vector Search. If the relevant chunk is ranked 51st or lower by Vector Search, it is never seen by the reranker. The design implication is that the initial Vector Search `num_results` (retrieval pool size) must be large enough to include all likely relevant chunks before reranking.
C) The statement is accurate — but this limitation is acceptable because Vector Search's approximate nearest neighbor algorithm guarantees that any chunk with cosine similarity above 0.7 to the query will always appear in the top-50 results.
D) The statement is inaccurate — rerankers use a different embedding space than Vector Search, so a chunk ranked 51st by Vector Search may rank 1st by the reranker; both systems are queried independently and their results are merged.

**Correct Answer:** B
**Explanation:** B is correct. The reranker is a second-stage filter, not an independent retrieval system. It receives only the candidates that Vector Search already returned (top-50 in this case). If the correct chunk is ranked 51st by Vector Search — even by the smallest cosine similarity margin — the reranker never sees it and cannot rescue it. The design implication is that the initial retrieval pool (`num_results`) must be generously sized to capture all potentially relevant chunks before the reranker applies its more precise scoring. A is wrong because rerankers in standard RAG architectures do not make additional retrieval calls to the Vector Search index — they operate purely on the already-retrieved candidate set. C is wrong because approximate nearest neighbor algorithms have no such guarantee — they trade some accuracy for speed, and chunks with borderline similarity may or may not appear in the top-50. D is wrong because the reranker and Vector Search use different scoring mechanisms (cross-encoder vs. bi-encoder), but they are not independent retrieval systems — the reranker receives only the Vector Search output; it does not query the index independently.
**Source:** Section 2: Data Preparation – Objective 8: Explain the role of re-ranking in the information retrieval process — docs.databricks.com (search: "Databricks Vector Search reranking")

---

### Question 18
**Difficulty:** Proficiency

A developer writes the following Spark code to prepare chunked data for Vector Search:

```python
df.write.format("delta").mode("overwrite").saveAsTable("main.docs.chunks")
```

Then creates the Vector Search index immediately. Three days later, 200 new chunks are added to the source Delta table using `df_new.write.format("delta").mode("append").saveAsTable("main.docs.chunks")`. The developer triggers a Vector Search sync and expects the 200 new chunks to appear in the index. Instead, the sync fails with a "Change Data Feed not enabled" error. What went wrong?

A) The `mode("overwrite")` used in the initial write destroyed and recreated the Delta table, which resets all table properties including `delta.enableChangeDataFeed = true` if it was previously set on the original table.
B) The `mode("append")` used for the new chunks created a separate Delta table partition that is not covered by the CDF property set on the main table, requiring a separate CDF enable statement for the new partition.
C) CDF was never enabled on the table before or after the initial write; the developer forgot to run `ALTER TABLE main.docs.chunks SET TBLPROPERTIES (delta.enableChangeDataFeed = true)` before creating the Vector Search index.
D) The Vector Search index requires CDF to be enabled on the Unity Catalog schema (`main.docs`), not on the individual table; the developer incorrectly applied CDF at the table level instead of the schema level.

**Correct Answer:** C
**Explanation:** C is correct. The most likely root cause is that CDF was never enabled on the table. The code shown (`write.format("delta")...saveAsTable()`) creates a Delta table but does not enable CDF. The Vector Search index was created without CDF being active, and when new data was appended and a sync was triggered, Vector Search detected the missing CDF property and threw the error. The fix is to run `ALTER TABLE main.docs.chunks SET TBLPROPERTIES (delta.enableChangeDataFeed = true)` after the initial table creation and before creating the index. A is wrong but is a relevant edge case: `mode("overwrite")` CAN reset table properties if it uses `overwriteSchema = true` or drops and recreates the table; however, in standard behavior `overwrite` mode replaces data files but preserves table metadata and properties. C is the most likely cause given the scenario. B is wrong because Delta Lake CDF is a table-level property — it applies to all partitions of the table uniformly; there is no per-partition CDF enablement. D is wrong because Unity Catalog does not have a schema-level CDF setting; CDF is configured at the individual Delta table level.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Enable Change Data Feed")

---

### Question 19
**Difficulty:** Proficiency

An enterprise RAG pipeline processes 500,000 legal documents. After filtering, chunking, and embedding, the `Precision@5 = 0.88` but `Recall@5 = 0.31`. A principal engineer states: "High precision with low recall is the worst failure mode for a legal RAG application." Why is low recall especially dangerous in this legal context, and what architectural change best addresses it?

A) Low recall means the chatbot frequently returns verbose answers with too much retrieved context (88% of retrieved chunks are relevant, creating information overload for the LLM), which is dangerous in legal contexts requiring concise citations.
B) Low recall means the system retrieves 88% relevant chunks but misses 69% of all relevant legal information that exists in the knowledge base — in legal contexts, missing a relevant precedent, clause, or exception could lead to legally incorrect guidance; increasing `num_results` and adding a reranker improves recall without sacrificing precision.
C) Low recall means 31% of all user queries fail to retrieve any results at all, which is dangerous because legal professionals receive empty answers for nearly 1 in 3 queries, requiring a fallback to manual document search.
D) Low recall indicates that the Delta table holding the chunks has a low Change Data Feed transaction log retention period, causing 69% of indexed chunks to expire and become unavailable to Vector Search queries.

**Correct Answer:** B
**Explanation:** B is correct. `Recall@5 = 0.31` means that for each query, only 31% of all truly relevant chunks in the knowledge base are being found in the top-5 results. In legal RAG, missing relevant information is catastrophic: an overlooked contract clause, missed legal precedent, or unstated exception could lead to legally incorrect advice with serious consequences. The fix is to increase the retrieval pool (`num_results`) so more candidates are retrieved initially, then apply a reranker to select the best 5 from a larger, higher-recall candidate set. A is wrong because high Precision@5 = 0.88 means 88% of what IS retrieved is relevant — this is not information overload but high precision retrieval; the problem is what's being missed, not what's being retrieved. C is wrong because Recall@k does not measure the percentage of queries that return zero results; it measures coverage of known relevant documents within the top-k results for queries that do return results. D is wrong because Recall@5 is a retrieval quality metric, not a Delta Lake storage metric; CDF log retention affects sync performance, not the retrieval recall of indexed content.
**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance — docs.databricks.com (search: "MLflow evaluate for RAG")

---

### Question 20
**Difficulty:** Proficiency

A RAG pipeline uses the following two-stage retrieval: Vector Search retrieves top-100 chunks, then a cross-encoder reranker scores them and passes top-5 to the LLM. After deployment, latency is 4.2 seconds per query (SLA: 2 seconds). Profiling shows: Vector Search = 0.3s, reranker = 3.7s, LLM = 0.2s. The bottleneck is clear. What architectural change best reduces latency while maintaining retrieval quality?

A) Replace the cross-encoder reranker with a second bi-encoder embedding model that scores all 100 chunks against the query using cosine similarity, which runs in parallel and is significantly faster than the cross-encoder.
B) Reduce the Vector Search initial retrieval from top-100 to top-10, which gives the reranker only 10 chunks to score instead of 100, reducing reranker compute time by ~90% while accepting a small recall trade-off.
C) Move the reranker to a dedicated Databricks Model Serving endpoint with GPU-backed autoscaling, so it processes all 100 chunks in parallel on GPU hardware rather than sequentially on CPU.
D) Eliminate the reranker entirely and rely solely on Vector Search's cosine similarity ranking, reverting to the original retrieval approach and accepting the quality reduction as the only option within the latency constraint.

**Correct Answer:** B
**Explanation:** B is correct. The reranker's 3.7s latency scales with the number of chunks it must score — cross-encoders process each query-chunk pair individually. Reducing the candidate pool from 100 to 10 reduces the reranker's work by ~90%, bringing estimated reranker time to ~0.37s and total latency to approximately 0.87s — well within the 2-second SLA. The trade-off is a modest decrease in recall (fewer candidates for the reranker to choose from), which the team must validate against quality requirements. A is wrong because a second bi-encoder (the same technology as Vector Search) simply re-ranks using cosine similarity — it does not achieve the precision improvement of a cross-encoder. Using a bi-encoder for reranking defeats the purpose of the reranking stage. C is wrong because while GPU-backed serving would improve throughput for many concurrent users, scoring 100 query-document pairs sequentially on GPU reduces latency somewhat but not by the ~85% needed to meet the 2-second SLA given the current architecture. D is wrong because eliminating the reranker should be the last resort; reducing the candidate pool (option B) achieves the latency target while preserving much of the quality benefit of reranking.
**Source:** Section 2: Data Preparation – Objective 8: Explain the role of re-ranking in the information retrieval process — docs.databricks.com (search: "Databricks Vector Search reranking" and "Foundation Model APIs cross-encoders")
