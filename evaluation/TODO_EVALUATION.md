# SmartShop AI - Future Evaluation TODO

This file is only a roadmap for future evaluation work.

No evaluation framework is implemented yet.

## Evaluation frameworks to explore

### 1. Ragas

Use Ragas mainly for evaluating the RAG pipeline.

Possible metrics:

- Faithfulness
- Answer Relevancy
- Context Precision
- Context Recall
- Context Relevancy

SmartShop use cases:

- Check whether PGVector retrieves the right product, review, or policy documents.
- Check whether the final answer is supported by retrieved context.
- Check whether the answer is relevant to the customer query.


### 2. LangSmith

Use LangSmith for tracing, debugging, datasets, and evaluation experiments.

Possible uses:

- Trace LangGraph workflow execution.
- See which agent was selected.
- Inspect agent handoffs.
- Inspect retrieved documents.
- Track tool calls.
- Track latency.
- Track token usage.
- Track LLM cost.
- Create evaluation datasets.
- Compare prompt or model experiments.
- Add LLM-as-a-Judge evaluators.

SmartShop use cases:

- Router evaluation.
- Agent trajectory evaluation.
- RAG debugging.
- Regression testing after prompt or model changes.


### 3. DeepEval

Use DeepEval for LLM, RAG, and agent evaluation.

Possible metrics:

- Answer Relevancy
- Faithfulness
- Contextual Precision
- Contextual Recall
- Contextual Relevancy
- Task Completion
- Tool Correctness

SmartShop use cases:

- Check whether the response answers the user query.
- Detect hallucinations.
- Evaluate whether retrieved context is useful.
- Check whether the correct agent/tool was used.
- Check whether the requested shopping task was completed.


## Metrics to add later

### Router / Agent metrics

- Routing Accuracy
- Tool Correctness
- Task Completion
- Agent Handoff Success Rate


### Retrieval / RAG metrics

- Recall@K
- Precision@K
- Context Precision
- Context Recall
- Context Relevancy


### Final answer metrics

- Answer Correctness
- Answer Relevancy
- Faithfulness / Groundedness
- Completeness


### Operational metrics

- Success Rate
- Error Rate
- Average Latency
- P95 Latency
- Token Usage
- Cost per Request


## Suggested future approach

Possible combination:

SmartShop
    |
    +-- LangSmith
    |     Tracing
    |     Experiments
    |     Agent workflow debugging
    |     Tokens and latency
    |
    +-- Ragas
    |     RAG retrieval evaluation
    |     Faithfulness
    |     Context quality
    |
    +-- DeepEval
          LLM quality
          Agent evaluation
          Task completion
          Tool correctness


## TODO

- [ ] Create a golden evaluation dataset.
- [ ] Add router accuracy tests.
- [ ] Add retrieval Recall@K and Precision@K.
- [ ] Try Ragas for RAG evaluation.
- [ ] Try LangSmith datasets and experiments.
- [ ] Try DeepEval metrics.
- [ ] Add LLM-as-a-Judge evaluation.
- [ ] Track latency and token cost.
- [ ] Compare evaluation results after prompt changes.
- [ ] Add evaluation checks to CI/CD later.
