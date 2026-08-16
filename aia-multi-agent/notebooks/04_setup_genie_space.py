# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Setup Genie Spaces (Multi-Domain)
# MAGIC Creates multiple Genie Spaces, each scoped to a specific business domain.
# MAGIC The Supervisor Agent uses the Context Index to semantically route user
# MAGIC questions to the best-matching space at runtime.
# MAGIC
# MAGIC **Domains covered:**
# MAGIC - Claims Analytics (claims counts, amounts, processing, fraud)
# MAGIC - Policy & Underwriting (premiums, renewals, lapse rates, product mix)
# MAGIC - Distribution & Channels (agent performance, channel contributions, partner metrics)
# MAGIC - Customer Analytics (customer segments, retention, demographics)
# MAGIC
# MAGIC **Note:** Genie Spaces can be created via the UI or API. This notebook
# MAGIC provides the configuration for setup. Space IDs are registered in the
# MAGIC Context Index (notebook 03) for semantic routing at runtime.

# COMMAND ----------

catalog = "aia_multi_agent_catalog"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Multi-Domain Genie Space Configurations

# COMMAND ----------

GENIE_SPACE_CONFIGS = [
    {
        "key": "genie_space_claims",
        "title": "Claims Analytics",
        "description": (
            "Ask questions about insurance claims across all AIA regions and products. "
            "Covers claim counts, amounts, processing times, approval rates, fraud analysis, "
            "customer segments, and policy premium trends."
        ),
        "tables": [
            f"{catalog}.gold.claims_summary",
            f"{catalog}.gold.fraud_analysis",
            f"{catalog}.silver.enriched_claims",
        ],
        "sample_questions": [
            "What is the total number of claims by region for the last 12 months?",
            "What is the average claim processing time by product category?",
            "Which regions have the highest fraud scores?",
            "Show me the monthly trend of hospitalization claims in Hong Kong",
            "What is the claim approval rate by claim type?",
            "How many suspicious claims were filed in Q4 2024?",
        ],
    },
    {
        "key": "genie_space_policies",
        "title": "Policy & Underwriting Analytics",
        "description": (
            "Ask questions about insurance policies, underwriting, and premium analytics. "
            "Covers premium volumes, policy counts, renewal rates, lapse rates, product mix, "
            "and underwriting performance across regions and product categories."
        ),
        "tables": [
            f"{catalog}.gold.policy_performance",
            f"{catalog}.silver.enriched_policies",
        ],
        "sample_questions": [
            "What is the total premium by distribution channel?",
            "Show me the policy renewal rate by region for this year",
            "Which product categories have the highest lapse rate?",
            "What is the month-over-month growth in new policy issuance?",
        ],
    },
    {
        "key": "genie_space_distribution",
        "title": "Distribution & Channels Analytics",
        "description": (
            "Ask questions about agent performance, distribution channels, and partner metrics. "
            "Covers agent productivity, sales pipeline, channel contribution percentages, "
            "commission analysis, and partner network performance."
        ),
        "tables": [
            f"{catalog}.gold.agent_performance",
        ],
        "sample_questions": [
            "Who are the top-performing agents by premium collected?",
            "What is the average policy count per agent by region?",
            "Show me channel contribution percentages for the last quarter",
        ],
    },
    {
        "key": "genie_space_customers",
        "title": "Customer Analytics",
        "description": (
            "Ask questions about customer segments, retention, demographics, and lifecycle. "
            "Covers customer segmentation, retention rates, claim frequency by segment, "
            "customer lifetime value, and demographic analysis."
        ),
        "tables": [
            f"{catalog}.silver.customer_360",
        ],
        "sample_questions": [
            "Which customer segments have the highest claim frequency?",
            "What is the retention rate by customer segment?",
            "Show me the demographic breakdown of our top-tier customers",
        ],
    },
]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Genie Spaces via API

# COMMAND ----------

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

created_spaces = {}

for config in GENIE_SPACE_CONFIGS:
    key = config["key"]
    title = config["title"]
    tables = config["tables"]
    description = config["description"]

    try:
        space = w.genie.create_space(
            title=title,
            description=description,
            table_identifiers=tables,
        )
        created_spaces[key] = space.space_id
        print(f"[OK] Created '{title}': {space.space_id}")
    except Exception as e:
        print(f"[WARN] '{title}' creation via SDK: {e}")
        print(f"       Please create manually via UI with tables: {', '.join(tables)}")
        created_spaces[key] = None

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Tables Are Accessible

# COMMAND ----------

all_tables = set()
for config in GENIE_SPACE_CONFIGS:
    all_tables.update(config["tables"])

for table in sorted(all_tables):
    try:
        count = spark.table(table).count()
        print(f"  {table}: {count} rows")
    except Exception as e:
        print(f"  {table}: NOT ACCESSIBLE — {str(e)[:80]}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("=" * 60)
print("Genie Spaces Summary")
print("=" * 60)
for config in GENIE_SPACE_CONFIGS:
    key = config["key"]
    space_id = created_spaces.get(key, "NOT CREATED")
    print(f"  {config['title']}: {space_id}")
print()
print("Next step: Run notebook 03_create_context_index.py to register")
print("these spaces in the Context Index for semantic routing.")
