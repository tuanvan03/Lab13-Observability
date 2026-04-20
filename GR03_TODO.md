# Lab 13 Observability: Action Items 🚀

Welcome to the lab! The template repository is currently intentionally incomplete. Your goal is to fill out the unfinished `TODO` sections throughout the codebase and successfully instrument the application safely for observability observability platform.

Here is your checklist to track progress:

## Phase 1: Fixing Distributed Context & Logging
- [ ] **1. Implement Correlation IDs (`app/middleware.py`)**
  - Clear `contextvars` to avoid cross-request leakage.
  - Generate a new `x-request-id` header (format: `req-<8-char-hex>`).
  - Bind the `correlation_id` using structlog's context manager.
  - Append the `x-request-id` back into the final Response headers.
- [ ] **2. Enrich Logs with Context (`app/main.py`)**
  - Inside the `@app.post("/chat")` route, bind context parameters before logging.
  - Include variables: `user_id_hash=hash_user_id(body.user_id), session_id=body.session_id, feature=body.feature, model=agent.model, env=os.getenv("APP_ENV", "dev")`.
- [ ] **3. Implement PII Scrubbing (`app/logging_config.py`)**
  - In `configure_logging()`, uncomment out the `scrub_event` processor.
  - Ensure the scrubber effectively redacts emails (`@`) and test credit card numbers (`4111`).

## Phase 2: Verification and Tools
- [ ] **4. Validate Local Setup**
  - Make a few request tests using `python scripts/load_test.py`.
  - Check the output in `data/logs.jsonl` to see if logs are rendered as proper JSON structs.
  - Run the validation script to verify grading requirements:
    ```bash
    python scripts/validate_logs.py
    ```

## Phase 3: Observability Stack (Tracing, Dashboards & Alerts)
- [ ] **5. Langfuse Tracing Verification**
  - Ensure Langfuse environment variables are defined properly in `.env`.
  - Send at least 10-20 requests to populate your traces graph.
  - Open Langfuse UI and verify traces exist with the `@observe` traces and payloads effectively captured.
- [ ] **6. Metric Dashboards**
  - Start designing a 6-panel dashboard using the output metrics. (See `docs/dashboard-spec.md` for specific panel requirements).
- [ ] **7. Create Alert Rules**
  - Review your `config/slo.yaml` to see SLI and SLO goals.
  - Configure equivalent threshold alerting rules inside `config/alert_rules.yaml`.
  - Optional: Use `python scripts/inject_incident.py` to simulate degradation and verify alerts practically fire off.

## Phase 4: Final Documentation
- [ ] **8. Finalize Report**
  - Collect evidence of your team's success in `docs/grading-evidence.md`.
  - Fill out the team submission template in `docs/blueprint-template.md`. 
