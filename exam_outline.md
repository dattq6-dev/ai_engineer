# Databricks Certified Generative AI Engineer Associate - Exam Outline

**Section 1: Design Applications – 14%**
* Design a prompt that elicits a specifically formatted response
* Select model tasks to accomplish a given business requirement
* Select chain components for a desired model input and output
* Translate business use case goals into a description of the desired inputs and outputs for the AI pipeline
* Define and order tools that gather knowledge or take actions for multi-stage reasoning
* Determine how and when to use Agent Bricks (Knowledge Assistant, Multiagent Supervisor, Information Extraction) to solve problems

**Section 2: Data Preparation – 14%**
* Apply a chunking strategy for a given document structure and model constraints
* Filter extraneous content in source documents that degrades quality of a RAG application
* Choose the appropriate Python package to extract document content from provided source data and format.
* Define operations and sequence to write given chunked text into Delta Lake tables in Unity Catalog
* Identify needed source documents that provide necessary knowledge and quality for a given RAG application
* Use tools and metrics to evaluate retrieval performance
* Design retrieval systems using advanced chunking strategies
* Explain the role of re-ranking in the information retrieval process

**Section 3: Application Development – 30%**
* Select Langchain/similar tools for use in a Generative AI application.
* Qualitatively assess responses to identify common issues such as quality and safety
* Select chunking strategy based on model & retrieval evaluation
* Augment a prompt with additional context from a user's input based on key fields, terms, and intents
* Create a prompt that adjusts an LLM's response from a baseline to a desired output
* Implement LLM guardrails to prevent negative outcomes
* Select the best LLM based on the attributes of the application to be developed
* Select an embedding model context length based on source documents, expected queries, and optimization strategy
* Select a model from a model hub or marketplace for a task based on model metadata/model cards
* Select the best model for a given task based on common metrics generated in experiments
* Utilize MLflow and Agent Framework for developing agentic systems
* Compare the evaluation and monitoring phases of the Gen AI application life cycle
* Enable multi-agent systems to leverage Genie Spaces or conversational API to retrieve data

**Section 4: Assembling and Deploying Applications – 22%**
* Code a chain using a pyfunc model with pre- and post-processing
* Control access to resources from model serving endpoints
* Code a simple chain according to requirements
* Choose the basic elements needed to create a RAG application: model flavor, embedding model, retriever, dependencies, input examples, model signature
* Register the model to Unity Catalog using MLflow
* Create and query a Vector Search index
* Identify how to serve an LLM application that leverages Foundation Model APIs
* Explain the key concepts and components of Mosaic AI Vector Search
* Identify batch inference workloads and apply `ai_query()` appropriately
* Configure vector search for a particular solution based on number of embeddings, update frequency, latency, and cost requirements.
* Configure a persistent datastore to store and retrieve intermediate memory or structured information.
* Apply CI/CD best practices such as updating a Vector Search index, promoting prompts across environments, and testing individual components of an agent.
* Integrate managed, external, and custom MCP servers based on a given application requirements
* Apply prompt version control and manage prompt lifecycle
* Develop an appropriate interactive user facing interface for an agent usage scenario (Apps, Slack, Teams, etc.)

**Section 5: Governance – 8%**
* Use masking techniques as guard rails to meet a performance objective
* Select guardrail techniques to protect against malicious user inputs to a Gen AI application
* Use legal/licensing requirements for data sources to avoid legal risk
* Recommend an alternative for problematic text mitigation in a data source feeding a GenAI application

**Section 6: Evaluation and Monitoring – 12%**
* Select an LLM choice (size and architecture) based on a set of quantitative evaluation metrics
* Select key metrics to monitor for a specific LLM deployment scenario
* Evaluate agent performance using MLflow scoring and tracing
* Use inference logging to assess deployed RAG application performance
* Use Databricks features to control LLM costs
* Use inference tables and Agent Monitoring to track a live LLM endpoint
* Identify evaluation judges that require ground truth
* Use AI Gateway (Inference Tables, Usage Tables, and rate limiting) to track an LLM or agent deployed via Agent Framework.
* Use Databricks custom Scorers for evaluating agents and LLMs
* Incorporate SME feedback to improve agent performance
