# Project Overview: Lab 13 - Observability 🔭

## 📖 Overview
This project is a FastAPI-based "Agent" application designed for a hands-on lab on **Monitoring, Logging, and Observability**. It aims to simulate a realistic scenario with unstructured text logging that needs to be upgraded to production-ready structured logging, metrics aggregation, tracing, and incident management.

The agent handles chat requests using a `mock_rag` implementation to retrieve documents and a `mock_llm` to generate responses. By working on this project, participants learn how to properly instrument an application with core observability tools for production readiness.

---

## 🔄 Workflow

1. **Client Request**: The FastAPI app receives a POST request at `/chat` containing a query, `user_id`, `session_id`, and `feature`.
2. **Middleware Interception**: The `CorrelationIdMiddleware` intercepts the request and is supposed to append a unique `x-request-id` to trace the entire lifecycle of the request.
3. **Log Context Enrichment**: `main.py` enriches logs with request-specific metadata, ensuring logs capture who is doing what (binding `user_id_hash`, `session_id`, etc.).
4. **Agent Execution**: The `LabAgent` executes the workflow:
   - Fetches mock retrieved documents.
   - Generates a response using `FakeLLM`.
   - Records latency, cost estimates, and calculates heuristic quality score.
   - Logs metrics natively and traces the execution in Langfuse.
5. **PII Scrubbing**: Structlog processing intercepts logs to automatically scrub sensitive Personal Identifiable Information (PII) before it is output to `data/logs.jsonl`.
6. **Response**: The final response returns the generated answer, along with latency, tokens, cost, and the correlation ID explicitly for verification purposes.

---

## 💡 Core Ideas

### 1. Structured JSON Logging (`structlog`)
Switching from unstructured string logs to robust JSON logs. Why? JSON is machine-readable. It allows enterprise log aggregation systems (like ELK/Datadog) to reliably parse, filter, and search logs using specific keys (e.g., `event="request_failed"`, `error_type="ValueError"`).

### 2. Context Propagation & Correlation IDs
A `correlation_id` allows requests to be tied together across distributed microservices. Using Python's `contextvars`, the app binds the correlation ID and user-specific metadata (like session or feature type) natively to all log statements emitted during that specific web request lifecycle, preventing cross-request log leakage.

### 3. PII Scrubbing
A required middleware layer in the logging pipeline that detects and masks sensitive data (like emails, credit cards, or internal names) before the log is physically written to disk or sent to an aggregation service.

### 4. Distributed Tracing (`Langfuse`)
Through `@observe()` wrappers, the app visualizes AI operations. Rather than just capturing a flat list of logs, Tracing creates a tree diagram (Spans), helping root-cause latency bottlenecks, capture full inputs/outputs of an LLM prompt, and map the exact journey of an API request natively.

### 5. Metrics & Alerting
Generating golden signals (Latency, Traffic, Errors, Cost). Using mock SLA incidents (`/incidents`), developers simulate what it looks like when a system is degrading, allowing them to verify alert rules properly trigger based strictly on objective metric thresholds.
