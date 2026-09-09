### Question 41
**Difficulty:** Beginner

A developer needs to split a Markdown knowledge base article into chunks. The article uses `#` for the main title and `##` for major sections. They want each major section to be one chunk. Which chunking tool and split parameter should they use?

A) Use Python's `str.split('\n\n')` to split on double newlines, which corresponds to paragraph boundaries in Markdown and keeps each paragraph as a separate chunk regardless of header level.
B) Use LangChain's `MarkdownHeaderTextSplitter` configured to split on `##` headers, which produces one chunk per major section while keeping the section content together and adding the section title as metadata.
C) Use `PyPDF2`'s page-based splitter to create one chunk per page, which aligns well with Markdown structure since each major section typically occupies a full rendered page.
D) Use `pytesseract` to OCR-render the Markdown file as an image and then split on visual whitespace gaps between sections, which detects structural boundaries regardless of the underlying text format.

**Correct Answer:** B
**Explanation:** B is correct. LangChain's `MarkdownHeaderTextSplitter` is designed exactly for this use case — it takes a list of header levels to split on (e.g., `[("##", "Section")]`) and produces one chunk per section, with the section title added as chunk metadata. This directly fulfills the requirement of one chunk per major section while preserving content integrity. A is wrong because double-newline splitting creates paragraph-level chunks, not section-level chunks — a major section with multiple paragraphs would be split into multiple chunks against the requirement. C is wrong because `PyPDF2` is a PDF parsing library, not a Markdown processing tool; Markdown files are plain text and do not have pages. D is wrong because `pytesseract` is an OCR tool for image-based text — applying it to a Markdown file (which is already machine-readable text) adds unnecessary complexity, accuracy loss, and computational overhead.
**Source:** Section 2: Data Preparation – Objective 1: Apply a chunking strategy for a given document structure — docs.databricks.com (search: "Data preparation for RAG applications")

---

### Question 42
**Difficulty:** Beginner

A developer writes a chunk to a Unity Catalog Delta table with the column `chunk_text`. When they create a Databricks Vector Search index on this table, what additional column is automatically added to the index and what does it represent?

A) A `chunk_summary` column is automatically added by Vector Search, which stores a 1-sentence LLM-generated summary of each chunk for fast keyword matching during retrieval.
B) A `vector` or embedding column is automatically computed and stored by the Vector Search service — it contains the high-dimensional numerical array (embedding) of each `chunk_text`, enabling semantic similarity search.
C) A `relevance_score` column is automatically added, containing a pre-computed relevance score between 0 and 1 that the index uses to rank chunks at query time without performing real-time vector computation.
D) A `doc_hash` column is automatically added containing an MD5 hash of each `chunk_text`, which Vector Search uses as the primary deduplication key to prevent duplicate chunks from being stored in the index.

**Correct Answer:** B
**Explanation:** B is correct. When a Databricks Vector Search index is created on a Delta table containing a text column, the Vector Search service automatically computes and stores the vector embedding for each row's text using the configured embedding model. This embedding column is the foundation of semantic similarity search — at query time, the query is also embedded and compared against stored embeddings using approximate nearest neighbor algorithms. A is wrong because Vector Search does not automatically generate LLM summaries of chunks; no LLM processing occurs at index creation time in standard configurations. C is wrong because there is no pre-computed static relevance score — relevance is computed dynamically at query time by comparing the query vector against stored chunk vectors, as relevance depends on the specific query. D is wrong because while `id` is used for deduplication and change tracking, Vector Search does not automatically add an MD5 hash column; deduplication is handled through the unique primary key column that the developer provides.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Create a Mosaic AI Vector Search index")

---

### Question 43
**Difficulty:** Beginner

A developer has source documents as HTML files, PDFs, and plain `.txt` files. They want a unified extraction pipeline that handles all three formats without writing separate parsing code for each. Which library best satisfies this requirement?

A) `PyPDF2` — because it is the most widely used document extraction library and implicitly supports HTML and TXT files as fallback formats when the primary PDF parsing mode does not detect PDF metadata.
B) `beautifulsoup4` — because its HTML parser can handle any file extension by reading the raw bytes of PDF and TXT files as if they were HTML documents, producing consistent text output across all three formats.
C) `unstructured` — because it is a multi-format document parsing library with native support for HTML, PDF, and plain text files, providing a unified API that auto-detects format and returns structured text elements.
D) `pytesseract` — because it renders each file format to a JPEG image internally before performing OCR, producing consistent machine-readable text from any source format including HTML, PDF, and TXT.

**Correct Answer:** C
**Explanation:** C is correct. `unstructured` is the only library among the options that natively handles all three formats (HTML, PDF, plain text) through a unified `partition()` function that auto-detects file format and routes to the appropriate parser. This eliminates the need to write separate parsing code for each format. A is wrong because `PyPDF2` is a PDF-specific library — it cannot parse HTML or TXT files; using it on non-PDF files produces errors or empty output. B is wrong because `beautifulsoup4` is an HTML/XML parser only — it cannot meaningfully parse binary PDF files; treating a PDF as HTML would produce garbled output from the binary data. D is wrong because `pytesseract` renders documents to images for OCR only when dealing with image-based content; applying OCR to digital HTML and TXT files (which already have machine-readable text) would be lossy, slow, and produce unnecessary accuracy errors.
**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package — docs.databricks.com (search: "RAG reference architecture data preparation")

---

### Question 44
**Difficulty:** Beginner

What is the purpose of the `chunk_overlap` parameter in a fixed-size chunking configuration?

A) `chunk_overlap` controls how many chunks from adjacent documents are combined together into one super-chunk, enabling the retriever to always return multi-document context to the LLM.
B) `chunk_overlap` specifies the number of tokens that are duplicated between consecutive chunks, preserving context at chunk boundaries so that sentences or ideas split by the chunk boundary appear in both adjacent chunks.
C) `chunk_overlap` sets the minimum number of meaningful tokens a chunk must contain before it is written to the Delta table; chunks with fewer tokens than the overlap value are automatically discarded.
D) `chunk_overlap` defines the maximum allowed similarity between two adjacent chunks — if their cosine similarity exceeds this value, one chunk is dropped to prevent the Vector Search index from storing near-duplicate embeddings.

**Correct Answer:** B
**Explanation:** B is correct. `chunk_overlap` is the number of tokens shared between the end of one chunk and the beginning of the next chunk. For example, with `chunk_size=512` and `chunk_overlap=64`, the last 64 tokens of chunk N become the first 64 tokens of chunk N+1. This ensures that a sentence or concept that falls at the boundary between two chunks is fully represented in both, preventing context loss at chunk boundaries. A is wrong because `chunk_overlap` operates within a single document's chunking, not across different documents; it does not combine chunks from different documents. C is wrong because `chunk_overlap` is about boundary token duplication, not a minimum token threshold for filtering; a separate `min_chunk_size` parameter would handle filtering of small chunks. D is wrong because `chunk_overlap` is a text processing parameter set before embedding; it has nothing to do with cosine similarity or deduplication in the vector index.
**Source:** Section 2: Data Preparation – Objective 1: Apply a chunking strategy — docs.databricks.com (search: "Data preparation for RAG applications")

---

### Question 45
**Difficulty:** Beginner

A company stores its source documents in Databricks Volumes as PDF files. What is the correct pipeline sequence to make these documents searchable via a Databricks Vector Search index?

A) Create the Vector Search index directly on the Volume path — Vector Search can automatically detect, parse, and embed PDF files stored in Volumes without any intermediate processing steps.
B) Extract text from PDFs using a parsing library (e.g., `unstructured`), chunk the extracted text, write the chunks to a Unity Catalog Delta table with CDF enabled, then create the Vector Search index on the Delta table.
C) Upload the PDF files to Databricks Model Serving as binary artifacts, which automatically vectorizes and indexes them — then configure the Vector Search index to query the Model Serving artifact store.
D) Convert the PDFs to Delta tables using the Databricks Auto Loader PDF connector, which automatically detects PDF structure and creates one Delta row per paragraph, ready for immediate Vector Search indexing.

**Correct Answer:** B
**Explanation:** B is correct. Databricks Vector Search requires a Delta Lake table as its data source — it cannot directly index files from Volumes. The correct pipeline is: (1) Use a parsing library (`unstructured`, `PyPDF2`, etc.) to extract text from PDFs in the Volume, (2) apply a chunking strategy to produce text chunks, (3) write chunks as rows to a Unity Catalog Delta table with CDF enabled, (4) create a Vector Search index on the Delta table. A is wrong because Vector Search does not have a native capability to directly read and parse PDF files from Volumes; it requires Delta tables as the source. C is wrong because Databricks Model Serving is for deploying ML models as REST APIs — it is not an artifact indexing service and has no automatic vectorization pipeline for documents. D is wrong because Auto Loader is designed to ingest structured and semi-structured data (CSV, JSON, Parquet, Avro) — there is no built-in PDF connector that automatically converts PDFs to paragraph-level Delta rows.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Create a Mosaic AI Vector Search index")

---

### Question 46
**Difficulty:** Intermediate

A developer discovers that their RAG chatbot is returning wrong answers specifically for topics that span multiple sections of a long document. For example, "What are the steps to set up SSO?" returns incomplete steps because step 1 is in the "Prerequisites" section and steps 2–5 are in the "Configuration" section — split across multiple chunks. What chunking strategy best addresses this multi-section problem?

A) Use smaller chunk sizes (e.g., 100 tokens) so that more chunks are retrieved in the top-k, increasing the probability that all prerequisite and configuration section chunks appear in the retrieved set simultaneously.
B) Use document-aware chunking at a higher structural level (e.g., split only at the top-level `#` document header instead of `##` section headers), so that all sections of a single document remain in one larger chunk that the LLM can read end-to-end.
C) Use a sliding window approach where every chunk overlaps by 90% of its length with the previous chunk, effectively creating near-duplicate chunks for every token position to ensure no cross-section content is missed.
D) Add a `related_sections` metadata column to each chunk that lists the section IDs of adjacent sections, and modify the retriever to automatically fetch adjacent sections when any section chunk is retrieved.

**Correct Answer:** B
**Explanation:** B is correct. When topics span multiple document sections, splitting at a lower granularity (e.g., `##` headers) creates inter-section dependency that no retriever can reliably bridge. The fix is to chunk at a higher structural level — splitting only on the document title (`#`) keeps all sections of one document together in a single (larger) chunk. The trade-off is larger chunks with more mixed content, but for documents where cross-section queries are common, it is the correct architectural choice. This may require combining with a size-limiting second split if the document exceeds the token limit. A is wrong because using smaller chunks (100 tokens) creates more fragmented chunks with even less context per chunk — more fragments does not solve the cross-section dependency problem. C is wrong because 90% overlap creates massive data redundancy (a 512-token chunk with 90% overlap produces chunks every 51 tokens), exploding storage and index size without meaningfully improving the multi-section retrieval problem. D is wrong because adding related_sections metadata and modifying the retriever requires significant custom infrastructure code and is fragile — the prerequisite for this approach is accurate section relationship metadata, which is itself complex to maintain.
**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies — docs.databricks.com (search: "Advanced chunking strategies RAG")

---

### Question 47
**Difficulty:** Intermediate

A developer runs the following code to prepare a Vector Search source table:

```python
spark.sql("""
  CREATE TABLE IF NOT EXISTS main.docs.chunks 
  (id BIGINT, chunk_text STRING)
  TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")
```

Is this approach correct for enabling CDF? Are there any risks with the `id BIGINT` column type?

A) The code is incorrect — CDF must be enabled separately with `ALTER TABLE` after table creation; including it in `CREATE TABLE TBLPROPERTIES` silently fails and CDF is not actually enabled.
B) The code is correct — CDF can be enabled at table creation time via `TBLPROPERTIES`. However, `id BIGINT` risks column type conflicts if the source system generates string-format IDs (e.g., UUIDs), which must be cast to BIGINT or the pipeline will fail with type errors.
C) The code is correct and the `id BIGINT` type is always appropriate since Vector Search requires integer primary keys; string-type IDs are not supported as primary key columns for Vector Search indexes.
D) The code is incorrect — CDF requires the source table to use Delta Lake format v3 or higher; specifying `TBLPROPERTIES` at creation time only works with format v3, and Unity Catalog tables default to format v1.

**Correct Answer:** B
**Explanation:** B is correct. Including `delta.enableChangeDataFeed = true` in the `TBLPROPERTIES` at `CREATE TABLE` time is a fully valid and supported approach — CDF is activated from the first write. However, `id BIGINT` is a risk: if source document IDs are UUID strings (e.g., "a1b2c3d4-..."), casting them to BIGINT would fail or produce incorrect values. The developer should use `id STRING` if the source IDs are not guaranteed to be integers. Databricks Vector Search supports both string and integer primary key column types. A is wrong because CDF can be enabled either at creation time (via `TBLPROPERTIES` in `CREATE TABLE`) or after creation (via `ALTER TABLE`); both approaches are valid and supported. C is wrong because Databricks Vector Search supports string-type primary key columns — BIGINT is not the only accepted type. D is wrong because there is no "format version" prerequisite for CDF; CDF has been available in Delta Lake for years and works with the default table format in Unity Catalog.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Enable Change Data Feed" and "Create a Mosaic AI Vector Search index")

---

### Question 48
**Difficulty:** Intermediate

A team is evaluating whether to use a cross-encoder reranker or a bi-encoder re-scoring step as stage 2 after Vector Search retrieval. The application serves 500 queries per second. Which technical trade-off determines the correct choice?

A) Cross-encoders produce more accurate relevance scores but are computationally expensive (they process each query-document pair together); bi-encoder re-scoring is faster but less accurate (it scores query and documents independently). For 500 QPS, the latency cost of a cross-encoder on 50 candidates per query must be evaluated against the quality improvement.
B) Cross-encoders are always faster than bi-encoders at scale because they use precomputed document representations; bi-encoders recompute document embeddings at query time, making them slower for high-volume applications.
C) Bi-encoders produce more accurate reranking than cross-encoders at high query volumes because bi-encoders can be parallelized across GPU cores, while cross-encoders run sequentially on CPU only.
D) Cross-encoders and bi-encoders produce identical reranking quality for queries longer than 50 tokens; the choice only matters for very short queries (under 10 tokens) where cross-encoders have a slight advantage.

**Correct Answer:** A
**Explanation:** A is correct. This is the fundamental cross-encoder vs. bi-encoder trade-off: cross-encoders jointly encode query and document together, giving them access to fine-grained query-document interactions for high accuracy, but at the cost of running a separate forward pass for each candidate pair (O(n) compute per query). Bi-encoders encode query and documents separately (documents can be pre-encoded) and score by dot product — much faster but less precise because the joint attention mechanism is absent. At 500 QPS with 50 candidates each, a cross-encoder must perform 25,000 inference calls per second, which may exceed latency targets. The team must benchmark latency and quality for their specific throughput requirement. B is wrong because this reverses the trade-off: bi-encoders use precomputed document embeddings (stored in the index) and are faster; cross-encoders process query-document pairs jointly and are computationally more expensive. C is wrong because accuracy trade-off is the opposite — cross-encoders are more accurate than bi-encoder re-scoring because of their joint attention mechanism; accuracy claims in C are incorrect. D is wrong because the accuracy gap between cross-encoders and bi-encoders is not determined by query token length; cross-encoders consistently outperform bi-encoders across all query lengths.
**Source:** Section 2: Data Preparation – Objective 8: Explain the role of re-ranking — docs.databricks.com (search: "Databricks Vector Search reranking" and "Foundation Model APIs cross-encoders")

---

### Question 49
**Difficulty:** Intermediate

A developer adds document metadata (title, author, publication_date) as additional columns to the source Delta table used by Vector Search. A colleague asks: "Do these metadata columns affect the embedding computation?" What is the technically correct answer?

A) Yes — Vector Search automatically concatenates all string columns from the Delta table into the embedding input, so adding title and author columns increases the semantic richness of the embedding vector.
B) No — the embedding is computed only from the designated `chunk_text` column specified when creating the index. Metadata columns (title, author, publication_date) are stored in the index for filtering and retrieval but do not influence the embedding computation.
C) Yes — but only the `title` column is automatically appended to `chunk_text` before embedding; other metadata columns (author, publication_date) are stored separately without affecting the embedding.
D) No — metadata columns are not stored in the Vector Search index at all; they remain only in the source Delta table and must be joined back after retrieval using the `id` column to access metadata in the application.

**Correct Answer:** B
**Explanation:** B is correct. When creating a Databricks Vector Search index, you specify which column contains the text to embed (e.g., `source_column="chunk_text"`). Only this designated column's text is passed to the embedding model. Metadata columns (title, author, date) are stored alongside the embedding in the index for use as retrieval filters (e.g., `filters_json='{"author": "Jane Smith"}'`) or as returned metadata in results, but they do not contribute to the embedding vector itself. A is wrong because Vector Search does not automatically concatenate all string columns — only the explicitly designated `source_column` is embedded. Adding metadata columns to the table does not change what gets embedded. C is wrong because there is no automatic title-appending behavior; embedding input is strictly limited to the designated source column. D is wrong because metadata columns ARE stored in the Vector Search index alongside the embeddings — this is how metadata filtering works at query time without requiring a separate Delta table join.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Create a Mosaic AI Vector Search index")

---

### Question 50
**Difficulty:** Intermediate

A developer is evaluating retrieval quality using a 200-question test set. For each question, they know the exact chunk IDs that should be returned. They want to measure both "are the right chunks being retrieved?" AND "are they being returned in the right order?" Which combination of metrics should they compute?

A) `Precision@k` only — it captures both retrieval accuracy (whether right chunks are returned) and ranking quality (whether they are returned in the right order) in a single unified metric.
B) `Recall@k` and `Precision@k` together — Recall@k measures whether all relevant chunks are found, and Precision@k measures what fraction of returned chunks are relevant; together they capture coverage and accuracy but not ranking.
C) `Recall@k` and `nDCG@k` together — Recall@k measures whether all relevant chunks are found (coverage), and nDCG@k measures position-weighted relevance quality (ranking) — together they capture both retrieval completeness and ranking quality.
D) `MRR` (Mean Reciprocal Rank) only — it directly measures both the fraction of correctly retrieved chunks AND their rank positions, making it the single comprehensive metric for evaluating both retrieval and ranking simultaneously.

**Correct Answer:** C
**Explanation:** C is correct. The question requires two distinct measurements: (1) "Are the right chunks being retrieved?" is answered by Recall@k — it measures coverage (what fraction of known-relevant chunks appear in the top-k). (2) "Are they being returned in the right order?" is answered by nDCG@k — it measures position-weighted relevance (giving more credit to relevant chunks at higher ranks). Together, Recall@k and nDCG@k comprehensively cover both retrieval completeness and ranking quality. A is wrong because Precision@k measures what fraction of returned chunks are relevant (accuracy) but does not measure ranking quality — a Precision@5 of 0.8 is the same whether the 4 relevant chunks are at ranks 1–4 or ranks 2–5. B is wrong because while Recall@k and Precision@k together capture coverage and accuracy, they do not capture ranking quality — as noted, neither metric distinguishes whether relevant results appear at rank 1 or rank 10. D is wrong because MRR (Mean Reciprocal Rank) measures the rank of the FIRST relevant result only — it does not measure coverage (Recall) or the ordering of ALL relevant results.
**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance — docs.databricks.com (search: "MLflow evaluate for RAG")

---

### Question 51
**Difficulty:** Advanced

A developer instructs a junior engineer: "Add `@mlflow.trace(span_type='RETRIEVER')` to the retrieval function before the evaluation run." The junior engineer adds it to the wrong function — they add it to the LLM call wrapper instead of the retrieval function. What will happen when `mlflow.genai.evaluate()` runs the `RetrievalRelevance` scorer?

A) The scorer will raise a `SpanTypeConflict` exception because the `RETRIEVER` span type is exclusively reserved for Vector Search function calls; applying it to any other function violates MLflow's span type schema validation.
B) The scorer will not find a `RETRIEVER`-typed span in the expected location of the trace tree; it will look for retrieved documents in the span output and instead find the LLM's generated text, causing the scorer to fail or return null/nonsensical scores.
C) The scorer will automatically detect that the decorated function is an LLM call (based on the input/output format) and switch to using `AnswerRelevance` scoring instead of `RetrievalRelevance` scoring, adapting to the span content.
D) The scorer will work correctly because MLflow's `RetrievalRelevance` scorer reads all spans in the trace tree regardless of their type, averaging relevance scores across all captured inputs and outputs.

**Correct Answer:** B
**Explanation:** B is correct. MLflow's `RetrievalRelevance` scorer specifically looks for a span typed as `"RETRIEVER"` in the trace tree to find the retrieval inputs (the query) and outputs (the retrieved document chunks). If the `RETRIEVER` span type is applied to the LLM call wrapper instead, the span that MLflow finds in the `RETRIEVER` slot will contain the LLM's generated text as its output rather than document chunks. The scorer will either fail to parse the LLM output as retrieved documents, return null scores, or produce meaningless scores based on misidentified data. A is wrong because MLflow does not enforce which Python function a span type can be applied to — the `RETRIEVER` type is a semantic label, not a technical enforcement mechanism; misapplying it doesn't raise an exception. C is wrong because MLflow evaluation scorers do not automatically detect function types or switch scorer logic based on span content; they operate on whatever data is in the specified span. D is wrong because `RetrievalRelevance` specifically requires a `RETRIEVER`-typed span; it does not aggregate across all span types in the trace.
**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance — docs.databricks.com (search: "MLflow Tracing")

---

### Question 52
**Difficulty:** Advanced

A production RAG pipeline uses fixed-size chunking with 512 tokens and retrieves top-5 chunks. Engineers discover that for complex, multi-part user queries (e.g., "Compare the warranty terms, return policy, and price-matching guarantee for Product X"), individual chunks only cover one aspect each, causing the LLM to receive incomplete context. They decide to increase `num_results` from 5 to 15 to capture all three aspects. What new problem does this introduce, and what is the more architecturally sound fix?

A) Increasing `num_results` to 15 causes the Vector Search index query latency to increase by 3×, making the pipeline too slow for real-time use; the fix is to use a faster approximate nearest neighbor algorithm instead.
B) Increasing `num_results` to 15 sends 15 chunks (potentially 7,680 tokens) to the LLM, which may exceed the LLM's context window limit and dilute the LLM's attention across more content — the sound fix is multi-query decomposition: split the compound question into 3 sub-queries, retrieve top-5 for each, and deduplicate before assembling context.
C) Increasing `num_results` to 15 violates the Databricks Vector Search maximum results limit of 10 per query; the fix is to run two separate Vector Search queries with `num_results=7` and `num_results=8` and merge the results.
D) Increasing `num_results` to 15 causes the MLflow `RetrievalRelevance` scorer to time out because it must run an LLM judge 15 times instead of 5 times per query, making evaluation computationally infeasible for production use.

**Correct Answer:** B
**Explanation:** B is correct. Increasing `num_results` to 15 passes significantly more tokens (up to 15 × ~512 = 7,680 tokens) to the LLM. Modern LLMs have context window limits (even if large), and more content can dilute the LLM's attention, leading to reduced answer quality due to the "lost in the middle" phenomenon. The architecturally sound fix for multi-part queries is query decomposition: break "Compare warranty, return policy, and price-matching for Product X" into three focused sub-queries, retrieve top-5 for each, deduplicate overlapping chunks, and assemble a focused context set. This retrieves relevant context for each aspect without inflating the total context size unnecessarily. A is wrong because Databricks Vector Search is highly optimized for fast approximate nearest neighbor search; increasing `num_results` from 5 to 15 has minimal impact on query latency — the dominant latency factors are network and embedding computation. C is wrong because Databricks Vector Search supports retrieving significantly more than 10 results per query — there is no 10-result limit. D is wrong because evaluation run time is a development/testing concern, not a production concern; even if evaluation takes longer, it does not affect the production pipeline's correctness.
**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies — docs.databricks.com (search: "Advanced chunking strategies RAG")

---

### Question 53
**Difficulty:** Advanced

A developer's reranking stage uses a cross-encoder model to score 50 candidate chunks. The cross-encoder is deployed on a Databricks Model Serving CPU endpoint. Average reranker latency is 2.8 seconds per query. A performance engineer proposes: "We should use the cross-encoder's output scores as permanent metadata fields in the Vector Search index, so we don't need to run the reranker at query time." What is technically wrong with this proposal?

A) Storing pre-computed reranker scores in the Vector Search index is a valid optimization; the engineer's proposal is correct and would eliminate all reranker latency at query time.
B) Pre-computed cross-encoder scores are query-independent (computed once at index creation time), but cross-encoders are designed to score query-document relevance jointly — the score is specific to a particular query. A score computed during index creation is meaningless for a different user query at runtime.
C) Pre-computed scores would only work if stored in the Delta source table first, then synced to Vector Search; storing scores directly in the Vector Search index without going through the Delta source table violates the CDF sync architecture.
D) The proposal fails because Databricks Vector Search metadata fields can only store string or integer values; floating-point relevance scores from a cross-encoder cannot be stored as index metadata.

**Correct Answer:** B
**Explanation:** B is correct. This is the fundamental flaw in the proposal. A cross-encoder produces a relevance score for a specific (query, document) pair — the score changes with every different query. Pre-computing a score at index creation time would require knowing the query in advance, which is impossible for a live system serving diverse user queries. The scores computed at index time (without knowing the user's query) would be meaningless approximations. The reranker's value IS the query-dependent re-scoring — pre-computing it eliminates exactly the quality benefit it provides. A is wrong because the proposal is technically flawed for the reason explained in B; it is not a valid optimization. C is wrong because while CDF is required for Delta-to-VectorSearch sync, the proposal's flaw is not about the data pipeline architecture — it is about the fundamental query-dependence of cross-encoder scores. D is wrong because Databricks Vector Search metadata supports numeric (float) types; the proposal's flaw is not about data type limitations.
**Source:** Section 2: Data Preparation – Objective 8: Explain the role of re-ranking — docs.databricks.com (search: "Databricks Vector Search reranking" and "Foundation Model APIs cross-encoders")

---

### Question 54
**Difficulty:** Advanced

A team discovers that their RAG pipeline has high `Precision@5` (0.91) but very low `Recall@5` (0.28). They have 8 million chunks in the Vector Search index covering 200,000 source documents. What is the most likely architectural cause, and what change addresses it?

A) The embedding model is too large (7B parameters), making it overfit to training data and retrieve only chunks it "memorizes" from training — switching to a smaller 125M parameter embedding model improves generalization and recall.
B) The `num_results=5` setting is too low for a knowledge base of 8 million chunks — there may be 15–20 relevant chunks for complex queries, but only 5 are returned. Increasing `num_results` to 20–50, adding a reranker to select the best 5, improves recall while preserving precision.
C) The Delta source table uses partitioning by document ID, which causes Vector Search to only search within the partition matching the query's document ID — adding an `id` metadata filter to query all partitions simultaneously fixes the recall problem.
D) The Vector Search index sync is in `TRIGGERED` mode with manual syncs every 30 days — 72% of relevant chunks were added in the last 30 days and are not yet indexed. Switching to `CONTINUOUS` sync immediately restores full recall.

**Correct Answer:** B
**Explanation:** B is correct. `Recall@5 = 0.28` with `Precision@5 = 0.91` indicates that the 5 retrieved chunks are relevant (good precision) but many other relevant chunks are missed (low recall). With 8 million chunks and complex queries potentially having 15–20 truly relevant chunks, retrieving only 5 means the system misses most of them. The architectural fix is to increase `num_results` to 20–50 (a larger retrieval pool that has a higher probability of containing all relevant chunks), then apply a reranker to select the best 5 for the LLM — maintaining precision while dramatically improving recall. A is wrong because embedding model size does not directly cause low recall; a 7B parameter model is not more "memorized" than a smaller model in a way that would explain low recall on a private knowledge base. C is wrong because Vector Search performs global approximate nearest neighbor search across the entire index — it does not partition searches by document ID. D is wrong because if chunks are missing from the index due to sync lag, Precision@5 would also be low (wrong chunks would be retrieved) — the fact that precision is high (91%) confirms that indexed chunks are correct; the problem is retrieval coverage, not missing data.
**Source:** Section 2: Data Preparation – Objective 6 & 8: Retrieval metrics and re-ranking — docs.databricks.com (search: "MLflow evaluate for RAG" and "Databricks Vector Search reranking")

---

### Question 55
**Difficulty:** Advanced

A developer applies `unstructured`'s `partition_pdf()` to a financial report PDF and observes that numeric data from tables is extracted as `NarrativeText` elements instead of `Table` elements. This causes table rows to be chunked as prose sentences, losing the tabular structure. What is the root cause and the fix?

A) The financial report PDF uses non-standard fonts for table cells, which causes `unstructured`'s table detector to misclassify the cells as prose text. The fix is to convert the PDF to a standard font using a PDF editing tool before running `partition_pdf()`.
B) The `partition_pdf()` function defaults to text-layer extraction without table structure detection; enabling the table inference mode (e.g., `infer_table_structure=True` and using the `hi_res` strategy) instructs `unstructured` to use a table detection model to correctly classify and extract tabular elements.
C) `unstructured` cannot detect tables in financial PDFs because financial tables use merged cells and multi-column headers; the only fix is to manually export the PDF tables to CSV files and ingest them through a separate pipeline.
D) The PDF tables are using a `<div>`-based HTML table simulation instead of standard PDF table structures; switching to `beautifulsoup4` as the parser (which understands `<div>` layouts) correctly identifies and extracts the table data.

**Correct Answer:** B
**Explanation:** B is correct. `unstructured`'s `partition_pdf()` function operates in two modes: a fast default mode (`strategy="fast"`) that uses the PDF text layer for extraction and may not detect table structures correctly, and a high-resolution mode (`strategy="hi_res"`, `infer_table_structure=True`) that uses a computer vision-based table detection model (e.g., a YOLO-based table detector) to identify table regions and extract them as structured `Table` elements. Enabling `hi_res` mode with table inference is the correct fix. A is wrong because font type does not affect `unstructured`'s table detection — table detection in `hi_res` mode uses visual layout analysis, not font metadata. C is wrong because `unstructured` with `hi_res` mode and `infer_table_structure=True` is designed to handle complex financial tables with merged cells; manual CSV export adds unnecessary manual labor. D is wrong because PDF files do not contain HTML `<div>` elements — PDFs use a completely different internal format (PostScript-based), and `beautifulsoup4` cannot parse PDF binary content.
**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package — docs.databricks.com (search: "RAG reference architecture data preparation")

---

### Question 56
**Difficulty:** Proficiency

A data engineering team is building a production RAG data pipeline using Delta Live Tables (DLT). The pipeline must: (1) parse PDF documents from a Volume, (2) clean and filter content, (3) chunk text, and (4) write chunks to a Delta table with CDF enabled for Vector Search sync. What is the correct DLT implementation consideration that differs from a standard notebook pipeline?

A) DLT pipelines automatically enable Change Data Feed on all output Delta tables they create; the developer does not need to run `ALTER TABLE ... SET TBLPROPERTIES (delta.enableChangeDataFeed = true)` — DLT manages CDF automatically.
B) DLT pipelines cannot write to Unity Catalog Delta tables; the chunked output table must be written to the Hive metastore, and a separate job must copy it to Unity Catalog before Vector Search can index it.
C) DLT requires all Python transformation logic (PDF parsing, chunking) to be implemented using only Spark DataFrame operations; using non-Spark Python libraries like `unstructured` or `PyPDF2` inside DLT Python decorators is not supported.
D) DLT streaming tables cannot be configured with `TBLPROPERTIES` at table definition time; CDF must be enabled with `ALTER TABLE` after the first pipeline run completes and the table is physically created.

**Correct Answer:** A
**Explanation:** A is correct. One of Delta Live Tables' key features for streaming use cases is that it automatically enables Change Data Feed on all managed output tables. This is because DLT is inherently incremental and uses CDF internally for its own incremental processing. For Vector Search integration, this means DLT output tables are CDF-ready by default — a significant advantage over standard notebook pipelines that require the developer to manually enable CDF with `ALTER TABLE`. B is wrong because DLT fully supports Unity Catalog as the output metastore; writing to `catalog.schema.table` with `@dlt.table(name="catalog.schema.chunks")` is supported and recommended. C is wrong because DLT Python pipelines support arbitrary Python code within `@dlt.table` decorated functions, including non-Spark libraries like `unstructured` and `PyPDF2` via UDFs or Spark's `mapInPandas`; the only requirement is that the function returns a Spark DataFrame. D is wrong because DLT streaming tables do support `TBLPROPERTIES` at definition time via the `@dlt.table(table_properties={"delta.enableChangeDataFeed": "true"})` decorator argument — though as noted in A, DLT also enables CDF automatically.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Create a Mosaic AI Vector Search index" and "Enable Change Data Feed")

---

### Question 57
**Difficulty:** Proficiency

An organization's RAG pipeline serves a global team, and source documents are in English, French, German, and Japanese. The Vector Search index uses the Databricks `databricks-bge-large-en` embedding model. Users report poor retrieval for French, German, and Japanese queries even when relevant documents exist in those languages. What is the complete diagnosis and remediation?

A) The `databricks-bge-large-en` model is English-only; it produces low-quality embeddings for French, German, and Japanese text because it was trained on English data. The fix is to replace it with a multilingual embedding model (e.g., `text-embedding-3-large` or `paraphrase-multilingual-mpnet-base-v2`) that produces semantically aligned cross-lingual embeddings.
B) The retrieval failure is caused by the Delta table character encoding — French, German, and Japanese characters are stored as UTF-16 in the Delta table, but the embedding model requires UTF-8; the fix is to convert the Delta table's encoding to UTF-8.
C) The multilingual retrieval failure is caused by the Vector Search index's approximate nearest neighbor algorithm (HNSW) which can only handle Latin character embeddings; switching to an exact nearest neighbor search resolves the language limitation.
D) The fix is to add a language detection column to each chunk and apply a metadata filter at query time that restricts retrieval to chunks in the user's detected language, eliminating cross-language retrieval issues.

**Correct Answer:** A
**Explanation:** A is correct. The `databricks-bge-large-en` model (BGE Large English) is trained on English text and produces high-quality embeddings for English. Its embedding space is not aligned with French, German, or Japanese text — French/German/Japanese queries will not produce embedding vectors that are close to the corresponding French/German/Japanese document embeddings, causing retrieval failure. The fix is a multilingual embedding model that maps text in different languages to a shared semantic embedding space, enabling cross-lingual retrieval (English query → French document, etc.). B is wrong because Delta Lake stores strings as UTF-8 by default in Parquet files, and embedding models accept Python strings (already decoded from UTF-8); encoding is not the source of multilingual retrieval failure. C is wrong because the approximate nearest neighbor algorithm (HNSW or similar) operates on vectors of floating-point numbers — it has no awareness of the original character encoding or language; the language problem is in the embedding model, not the search algorithm. D is wrong because language-based metadata filtering restricts users to retrieving documents in their own language — this prevents cross-lingual retrieval (an English query finding a French document about the same topic) and does not address the core embedding quality issue.
**Source:** Section 2: Data Preparation – Objective 1 & 4: Chunking constraints and Delta Lake setup — docs.databricks.com (search: "Create a Mosaic AI Vector Search index" and "Data preparation for RAG applications")

---

### Question 58
**Difficulty:** Proficiency

A developer is designing the chunking strategy for a knowledge base of 10,000 API reference documents. Each document has a fixed structure: `Overview` (100–200 tokens), `Parameters` (50–500 tokens depending on API complexity), `Examples` (200–800 tokens), and `Error Codes` (100–300 tokens). Users query specific sections (e.g., "What parameters does the /users endpoint accept?"). What chunking design provides optimal retrieval precision?

A) Apply fixed-size 512-token chunking across all sections of all documents, treating the entire document as flat text and relying on the embedding model to implicitly learn the section structure from repeated section header tokens.
B) Apply section-aware chunking: use the document's section headers as split boundaries, creating separate chunks for `Overview`, `Parameters`, `Examples`, and `Error Codes` — each chunk prefixed with `[Document: /users API] [Section: Parameters]` metadata to enable targeted retrieval.
C) Apply Parent-Child chunking where each full API document is the parent and each token within the document is the child chunk, enabling the retrieval of the exact token that matches the query and providing the full document as LLM context.
D) Apply no chunking — store each entire API reference document as one chunk per document, relying on the LLM's 128K context window to process all 10,000 documents simultaneously for each user query.

**Correct Answer:** B
**Explanation:** B is correct. Given the consistent, predictable section structure of API reference documents and the highly targeted nature of user queries (users ask about specific sections, not entire documents), section-aware chunking is optimal. Each section becomes its own chunk, and the metadata prefix (`[Document: /users API] [Section: Parameters]`) enriches the embedding with contextual information that helps the retriever match section-specific queries. A query for "parameters of /users endpoint" will have high cosine similarity to the Parameters section chunk with its metadata prefix, producing highly precise retrieval. A is wrong because fixed-size chunking ignores the document structure and mixes section content across chunks, reducing precision for section-specific queries. C is wrong because using individual tokens as child chunks is computationally absurd and semantically meaningless; child chunks in Parent-Child should be semantically coherent (sentences or paragraphs), not individual tokens. D is wrong because Vector Search requires chunked text as rows in a Delta table; storing an entire document as one row would (a) likely exceed the embedding model's token limit and (b) reduce retrieval precision since the entire document's content is condensed into one embedding.
**Source:** Section 2: Data Preparation – Objective 1 & 7: Chunking strategy and advanced chunking — docs.databricks.com (search: "Advanced chunking strategies RAG")

---

### Question 59
**Difficulty:** Proficiency

A RAG pipeline serves a compliance team that queries a knowledge base of 500,000 regulatory documents. A compliance officer reports: "The chatbot sometimes references documents that were superseded by newer regulations — it mixes old and new guidance." Retrieval metrics show `Precision@5 = 0.88` and `Recall@5 = 0.79`. What is the correct diagnosis — is this a retrieval quality problem or a data governance problem — and what is the right fix?

A) This is a retrieval quality problem — `Precision@5 = 0.88` is below the 0.95 threshold required for regulatory use cases; improving the embedding model and adding a cross-encoder reranker will prevent outdated documents from being retrieved.
B) This is a data governance problem, not a retrieval quality problem — the retrieval metrics are healthy (88% precision, 79% recall), meaning the retriever correctly finds the most semantically similar documents. The issue is that superseded documents are still present and active in the knowledge base. The fix is a data lifecycle process: add a `status` column (`active`/`superseded`) to the source Delta table, update superseded documents to `status='superseded'`, and apply a metadata filter `status='active'` at query time.
C) This is a retrieval quality problem — `Recall@5 = 0.79` means 21% of relevant regulatory documents are missed per query; improving `num_results` to 25 and adding a reranker will surface all active regulations including the most recent ones.
D) This is a data governance problem that requires re-training the embedding model on only the current, active regulatory documents, so that embeddings for superseded documents become dissimilar to user queries and are naturally deprioritized by Vector Search.

**Correct Answer:** B
**Explanation:** B is correct. The retrieval metrics (Precision@5 = 0.88, Recall@5 = 0.79) indicate the retrieval system is performing well — it is correctly surfacing the most semantically similar documents. The problem is that "semantically similar" includes superseded documents that are topically related to the query (they cover the same regulation) but contain outdated guidance. This is not a retrieval failure — it is a data governance failure (outdated documents should not be in the active knowledge base). The correct fix is a data lifecycle management process: mark superseded documents with a `status='superseded'` flag and filter them out at query time. A is wrong because 0.88 precision is not the cause of the compliance issue — even perfect precision of 1.0 would not prevent semantically relevant but superseded documents from being retrieved if they remain active in the index. C is wrong for the same reason as A — improving recall retrieves more superseded documents, making the problem worse. D is wrong because re-training the embedding model is expensive and imprecise; metadata filtering is the correct, deterministic, and maintainable governance solution.
**Source:** Section 2: Data Preparation – Objective 5 & 6: Identify source documents and evaluate retrieval — docs.databricks.com (search: "Generative AI data preparation best practices" and "Mosaic AI Vector Search index")

---

### Question 60
**Difficulty:** Proficiency

A team is building a RAG pipeline for 200,000 scientific papers in biology. Each paper averages 15,000 tokens. They use Parent-Child chunking: each paper's abstract (200–500 tokens) as child chunks for vector search, with the full paper as parent context. A researcher reports: "When I ask detailed methodology questions, the answers are missing key experimental details." Investigation confirms the relevant methodology section exists in the full paper (parent) but is 4,000–6,000 tokens into the paper. What is the flaw in this design, and what is the fix?

A) The flaw is that the abstract (child chunk) correctly identifies the paper but the full paper (parent, ~15,000 tokens) exceeds most LLMs' useful context window — the LLM receives the full paper but loses the methodology section buried at 4,000–6,000 tokens in due to the "lost in the middle" phenomenon. The fix is to add methodology section chunks as additional child chunks, enabling direct retrieval of the methodology section as a focused child with the surrounding section (not full paper) as parent.
B) The flaw is that biology papers use domain-specific terminology that the embedding model cannot encode accurately; the abstract's general language creates embedding vectors that don't match methodology-specific queries. The fix is to fine-tune the embedding model on biology paper abstracts.
C) The flaw is that parent chunks (full papers at 15,000 tokens) exceed the Vector Search maximum document size of 8,192 tokens per chunk; storing full papers in Vector Search raises an exception. The fix is to limit parent chunks to 8,192 tokens by truncating papers at that limit.
D) The flaw is that the methodology section requires structured tabular data that the LLM cannot process from plain text; converting methodology sections to JSON structured format before storing in the Delta table enables the LLM to correctly interpret experimental parameters.

**Correct Answer:** A
**Explanation:** A is correct. This is a nuanced Parent-Child design flaw. The abstract correctly retrieves the right paper (high recall at the paper level) but the parent context (full 15,000-token paper) overwhelms the LLM — methodology details buried at positions 4,000–6,000 in a 15,000-token paper are subject to the "lost in the middle" phenomenon where LLMs attend less to content in the middle of very long contexts. The fix is hierarchical chunking with multiple child types: embed both the abstract AND the individual section chunks (abstract, introduction, methods, results, conclusion) as children. A methodology query then retrieves the methods child chunk directly, and its parent context is the methods section (~1,500–2,000 tokens) rather than the entire 15,000-token paper — giving the LLM focused, relevant context. B is wrong because while domain-specific terminology is a real concern, the described problem (methodology details in the parent paper not being surfaced) is a context position problem, not an embedding model vocabulary problem. C is wrong because the parent chunks (full papers) are stored in the Delta table, not in Vector Search — only the child embeddings (abstracts) are stored as vectors in the Vector Search index; full paper text length does not have a Vector Search size limit. D is wrong because the issue is context window positioning, not data format; biology methodology sections in plain text are fully processable by LLMs — converting them to JSON adds structure that the LLM doesn't need to understand the content.
**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies — docs.databricks.com (search: "Advanced chunking strategies RAG")
