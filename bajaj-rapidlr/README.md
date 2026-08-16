# Bajaj RapidLR — Agentic IT Support System

An AI-powered IT support system for the **RapidLR PL** data pipeline at Bajaj Finserv. Built on **Databricks**, **LangGraph**, and **LangChain**, the system autonomously investigates and resolves IT support tickets using Retrieval-Augmented Generation (RAG) and tool-calling agents.

## Overview

RapidLR PL is a data processing pipeline that routes leads through business rules to downstream systems (SFDC CRM, Dialer). This project provides:

- **Automated ticket triage** — classifies incoming tickets into investigation routes (log lookup, workflow, master maintenance)
- **RAG-powered knowledge retrieval** — retrieves similar past tickets and resolution patterns from a vector search index
- **Tool-calling agent** — a LangGraph ReAct agent that uses domain-specific tools to investigate issues and generate Root Cause Analysis (RCA) reports
- **Code analysis agent** — analyzes pipeline source code to identify root causes in business logic, filter rules, and configuration

## Architecture

```
IT Support Ticket
       │
       ▼
┌──────────────┐     ┌─────────────────────┐
│  RAG Retrieval│────▶│  Vector Search Index │
│  (Knowledge)  │     │  (past tickets + KB) │
└──────┬───────┘     └─────────────────────┘
       │
       ▼
┌──────────────┐     ┌─────────────────────┐
│  LangGraph   │────▶│  Domain Tools        │
│  ReAct Agent │     │  (log query, master  │
│              │◀────│   refresh, pipeline  │
└──────┬───────┘     │   check, etc.)       │
       │             └─────────────────────┘
       ▼
┌──────────────┐
│  RCA Report  │
│  Generation  │
└──────────────┘
```

### Investigation Routes

| Route | Trigger Signals | Tool Chain |
|-------|----------------|------------|
| **Log Lookup** | Specific log IDs, data not pushing to downstream, exclusion reasons | `query_log_view` → `analyze_exclusion_reason` → `check_control_flags` |
| **Workflow** | Pipeline failures, processor errors, data flow stoppages | `run_pipeline_check` → `check_upstream_source` → `query_log_view` |
| **Master Maintenance** | Table refresh/sync requests, cache memory updates | `update_master_table` → `refresh_master_table` → `send_email_notification` |

## Project Structure

```
Bajaj_RapidLR/
├── Main_Agent/
│   ├── RapidLR_Support.ipynb       # Main IT support agent (LangGraph workflow)
│   ├── Create_Knowledge_Base.ipynb  # Vector search index & KB setup
│   └── config.yml                   # Configuration (not tracked — contains secrets)
├── Code_Agent/
│   ├── nb0_CreateIndexes.ipynb      # Create Delta table indexes for code data
│   ├── Step2_codeAgent.ipynb        # Code analysis agent for root cause investigation
│   ├── code_agent.ipynb             # Code agent (placeholder)
│   └── start copy.ipynb             # Experimental GitHub repo analysis agent
├── assets/
│   ├── IT Requests for RapidLR PL.docx  # IT request documentation
│   ├── IT_requests_RapidLR.csv          # Historical IT requests dataset
│   └── sample_log_files_rlr_pl.csv      # Sample log data
├── docs/
│   └── kb.json                      # Knowledge base (past tickets + resolution steps)
├── databricks.yml                   # Databricks Asset Bundle configuration
└── .gitignore
```

## Notebooks

### Main Agent

| Notebook | Description |
|----------|-------------|
| **RapidLR_Support.ipynb** | Core agentic workflow. Defines the `ITSupportState`, domain tools (10 tools), LangGraph ReAct agent nodes, and RCA report generation. Processes a ticket end-to-end. |
| **Create_Knowledge_Base.ipynb** | Loads the IT support knowledge base from `docs/kb.json`, creates a Delta table with document chunks, and sets up a Databricks Vector Search index with managed embeddings (`databricks-gte-large-en`). |

### Code Agent

| Notebook | Description |
|----------|-------------|
| **nb0_CreateIndexes.ipynb** | Builds Delta table indexes from repository code. Combines config files with business unit code to enable code-level search for root cause analysis. |
| **Step2_codeAgent.ipynb** | Code analysis agent that fetches code from Delta tables and uses an LLM to analyze filter logic, feature flags, and conditional returns to identify root causes. |
| **start copy.ipynb** | Experimental notebook exploring GitHub repo traversal using Pydantic AI and LangGraph agents. Supports multiple LLM providers (Databricks, OpenAI, Groq). |

## Agent Tools

The main support agent has access to 10 domain-specific tools:

| Tool | Description |
|------|-------------|
| `refresh_master_table` | Refresh/sync a master table in cache memory |
| `update_master_table` | Update configuration values in a master table |
| `query_log_view` | Query the log table using log IDs for eligibility/exclusion status |
| `check_downstream_integration` | Check SFDC CRM / Dialer connectivity |
| `check_upstream_source` | Check upstream data source availability |
| `analyze_exclusion_reason` | Investigate why records were excluded |
| `check_control_flags` | Verify control flags (`sendToSfdc`, `sfdcFlag`) in master tables |
| `run_pipeline_check` | Run health check on data pipelines |
| `send_email_notification` | Send email notifications to stakeholders |
| `update_devops_ticket` | Update Azure DevOps ticket with investigation findings |

## Tech Stack

- **Databricks** — Workspace, Delta tables, Vector Search, Foundation Model APIs
- **LangGraph** — ReAct agent orchestration with stateful workflows
- **LangChain** — LLM abstraction, tool definitions, document retrieval
- **Databricks Vector Search** — Hybrid search over knowledge base embeddings
- **Foundation Models** — `databricks-claude-3-7-sonnet` (primary LLM), `databricks-gte-large-en` (embeddings)
- **PySpark** — Data processing for Delta tables and log views

## Setup

### Prerequisites

- Databricks workspace with access to Vector Search and Foundation Model APIs
- Python 3.10+

### Configuration

1. Copy the config template and add your credentials:
   ```bash
   cp "config copy.yml" Main_Agent/config.yml
   ```

2. Update `Main_Agent/config.yml` with your Databricks host and token:
   ```yaml
   databricks:
     host: "https://your-workspace.cloud.databricks.com"
     token: "your-databricks-token"
   ```

3. Alternatively, set environment variables:
   ```bash
   export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
   export DATABRICKS_TOKEN="your-token"
   ```

### Running the Notebooks

1. **Create the Knowledge Base** — Run `Main_Agent/Create_Knowledge_Base.ipynb` first to set up the Vector Search index
2. **Create Code Indexes** — Run `Code_Agent/nb0_CreateIndexes.ipynb` to set up code search tables
3. **Run the Support Agent** — Run `Main_Agent/RapidLR_Support.ipynb` to process IT support tickets
4. **Run the Code Agent** — Run `Code_Agent/Step2_codeAgent.ipynb` for code-level root cause analysis

## Key Data Assets

| Asset | Type | Description |
|-------|------|-------------|
| `agentic_ai.langgraph.it_support_kb_chunks` | Delta Table | Knowledge base document chunks |
| `agentic_ai.langgraph.it_support_kb_index` | Vector Search Index | Hybrid search index over KB |
| `agentic_ai.langgraph.sample_log_files_rlr_pl` | Log View | RapidLR PL processing logs |
| `main.sandesk4.git_index_raw` | Delta Table | Indexed repository code files |

## License

This project is proprietary to Bajaj Finserv. All rights reserved.
