import json

cells = []

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """# EPOWER Energy Intelligence Demo Setup

**A Hands-On Lab for Snowflake AI Capabilities**

---

## Welcome!

This notebook guides you through setting up a comprehensive **Snowflake Intelligence** demo for a German Energy Retail (B2C) use case. By the end of this lab, you'll have:

- A complete data warehouse with dimension and fact tables
- **Semantic Views** for natural language querying with Cortex Analyst
- **Cortex Search Services** for RAG over documents and structured data
- A **Snowflake Intelligence Agent** that combines all capabilities

### How to Use This Notebook

You can either:
- **Run all cells** sequentially for a quick setup (~10 minutes)
- **Run cell-by-cell** to learn about each concept as you go

### Prerequisites

- ACCOUNTADMIN role access (or equivalent privileges)
- A Snowflake account with Cortex features enabled"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """## Table of Contents

1. [Introduction to EPOWER Demo](#1-introduction)
2. [Role & Warehouse Setup](#2-role-warehouse-setup)
3. [Database & Schema Creation](#3-database-schema)
4. [Git Integration](#4-git-integration)
5. [Data Model - Dimension Tables](#5-dimension-tables)
6. [Data Model - Fact Tables](#6-fact-tables)
7. [Data Loading from Git Repository](#7-data-loading)
8. [Semantic Views for Cortex Analyst](#8-semantic-views)
9. [Unstructured Data Processing](#9-unstructured-data)
10. [Cortex Search Services](#10-cortex-search)
11. [Snowflake Intelligence Agent](#11-agent)
12. [Verification & Next Steps](#12-verification)"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 1. Introduction to EPOWER Demo <a id="1-introduction"></a>

### The Business Scenario

**EPOWER** is a fictional German energy provider offering:

| Product Category | Description |
|-----------------|-------------|
| **Strom & Gas** | Traditional electricity and gas tariffs |
| **Future Energy Home** | Solar panels, heat pumps, battery storage |
| **Smart Home** | Smart meters, energy management systems |
| **E-Mobility** | Wallbox charging stations, EV tariffs |

### What We're Building

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     SNOWFLAKE INTELLIGENCE AGENT                        │
│                    (Natural Language Interface)                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
        ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
        │ CORTEX ANALYST │  │ CORTEX SEARCH  │  │  WEB SCRAPER   │
        │  (Text-to-SQL) │  │     (RAG)      │  │  (Live Data)   │
        └────────────────┘  └────────────────┘  └────────────────┘
```

### Key Snowflake Features Demonstrated

| Feature | Purpose |
|---------|----------|
| **Git Integration** | Version-controlled data and code |
| **Semantic Views** | Business-friendly data modeling for AI |
| **Cortex Analyst** | Natural language to SQL conversion |
| **Cortex Search** | Vector search over documents |
| **Cortex Parse** | PDF/document parsing |
| **Intelligence Agent** | Multi-tool AI orchestration |"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 2. Role & Warehouse Setup <a id="2-role-warehouse-setup"></a>

### Concept: Role-Based Access Control (RBAC)

Snowflake uses **roles** to manage permissions. We'll create a dedicated role for this demo that has all necessary privileges while following the principle of least privilege.

**Best Practice**: Always use a dedicated role for demos/projects rather than ACCOUNTADMIN for day-to-day work."""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": "-- Switch to accountadmin to create resources\nUSE ROLE accountadmin;"
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": "-- Create Snowflake Intelligence object (account-level resource for agents)\nCREATE SNOWFLAKE INTELLIGENCE IF NOT EXISTS snowflake_intelligence_object_default;"
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Create a dedicated role for this demo
CREATE OR REPLACE ROLE EPOWER_ROLE;

-- Grant the role to current user
SET current_user_name = CURRENT_USER();
GRANT ROLE EPOWER_ROLE TO USER IDENTIFIER($current_user_name);

-- Grant necessary account-level privileges
GRANT CREATE DATABASE ON ACCOUNT TO ROLE EPOWER_ROLE;"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """### Concept: Virtual Warehouses

A **Virtual Warehouse** provides the compute resources to execute queries. Key features:

- **AUTO_SUSPEND**: Automatically pauses after idle time (saves credits)
- **AUTO_RESUME**: Automatically starts when queries arrive
- **Elastic Scaling**: Can resize without downtime

We use **XSMALL** for this demo - sufficient for our data volumes and cost-effective."""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Create a dedicated warehouse for the demo
CREATE OR REPLACE WAREHOUSE EPOWER_COMPUTE 
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;

GRANT USAGE ON WAREHOUSE EPOWER_COMPUTE TO ROLE EPOWER_ROLE;"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Set default role and warehouse for convenience
ALTER USER IDENTIFIER($current_user_name) SET DEFAULT_ROLE = EPOWER_ROLE;
ALTER USER IDENTIFIER($current_user_name) SET DEFAULT_WAREHOUSE = EPOWER_COMPUTE;

-- Switch to demo role
USE ROLE EPOWER_ROLE;"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 3. Database & Schema Creation <a id="3-database-schema"></a>

### Concept: Database Organization

Snowflake uses a three-tier namespace: `DATABASE.SCHEMA.OBJECT`

```
EPOWER_DEMO (Database)
    └── EPOWER_GOLD (Schema)
            ├── Tables
            ├── Semantic Views
            ├── Cortex Search Services
            └── Functions/Procedures
```"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Create database and schema
CREATE OR REPLACE DATABASE EPOWER_DEMO;
USE DATABASE EPOWER_DEMO;

CREATE SCHEMA IF NOT EXISTS EPOWER_GOLD;
USE SCHEMA EPOWER_GOLD;"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """### File Format Definition

A **File Format** defines how Snowflake should parse incoming data files. This is essential for CSV ingestion."""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Create file format for CSV files
CREATE OR REPLACE FILE FORMAT CSV_FORMAT
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    RECORD_DELIMITER = '\\n'
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    TRIM_SPACE = TRUE
    ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
    ESCAPE = 'NONE'
    ESCAPE_UNENCLOSED_FIELD = '\\\\'
    DATE_FORMAT = 'YYYY-MM-DD'
    TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'
    NULL_IF = ('NULL', 'null', '', 'N/A', 'n/a');"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 4. Git Integration <a id="4-git-integration"></a>

### Concept: Snowflake Git Integration

Snowflake can integrate directly with Git repositories, enabling:

- **Version-controlled data**: CSV files, SQL scripts, notebooks
- **Direct file access**: Query files directly from the Git repository stage
- **DevOps workflows**: CI/CD for data pipelines

**Architecture:**
```
GitHub Repository ──► API Integration ──► Git Repository Object ──► Stage Path
                                                                      │
                                              @REPO/branches/main/file.csv
```

**Key Benefit**: No need for intermediate staging - load data directly from Git!"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Create API integration for Git access (requires ACCOUNTADMIN)
USE ROLE accountadmin;

CREATE OR REPLACE API INTEGRATION git_api_integration_energy
    API_PROVIDER = git_https_api
    API_ALLOWED_PREFIXES = ('https://github.com/jojrg/')
    ENABLED = TRUE;

GRANT USAGE ON INTEGRATION git_api_integration_energy TO ROLE EPOWER_ROLE;"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """USE ROLE EPOWER_ROLE;
USE DATABASE EPOWER_DEMO;
USE SCHEMA EPOWER_GOLD;

-- Create Git repository connection
CREATE OR REPLACE GIT REPOSITORY EPOWER_DEMO_REPO
    API_INTEGRATION = git_api_integration_energy
    GIT_CREDENTIALS = null
    ORIGIN = 'https://github.com/jojrg/Snowflake_AI_DEMO.git';

-- Fetch latest from remote
ALTER GIT REPOSITORY EPOWER_DEMO_REPO FETCH;"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Verify: List files in the repository
LIST @EPOWER_DEMO_REPO/branches/main/demo_data/ PATTERN = '.*\\.csv';"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """### Internal Stage for Unstructured Documents

While we can load CSVs directly from Git, for **Cortex Parse** (PDF processing) and **Cortex Search**, we need an internal stage with directory table enabled."""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Create internal stage for unstructured documents (needed for Cortex Parse)
CREATE OR REPLACE STAGE EPOWER_STAGE
    FILE_FORMAT = CSV_FORMAT
    COMMENT = 'Internal stage for Energy demo unstructured documents'
    DIRECTORY = (ENABLE = TRUE)
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

-- Copy unstructured documents from Git to internal stage
COPY FILES INTO @EPOWER_STAGE/unstructured_docs/ 
FROM @EPOWER_DEMO_REPO/branches/main/unstructured_docs/;

ALTER STAGE EPOWER_STAGE REFRESH;"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 5. Data Model - Dimension Tables <a id="5-dimension-tables"></a>

### Concept: Star Schema Design

We use a **Star Schema** - a classic data warehouse design pattern:

- **Dimension Tables**: Descriptive attributes (WHO, WHAT, WHERE, WHEN)
- **Fact Tables**: Measurable events/transactions (HOW MUCH, HOW MANY)

**Benefits:**
- Simple, intuitive queries
- Optimized for analytical workloads
- Perfect for Semantic Views and Cortex Analyst"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Product Category Dimension
CREATE OR REPLACE TABLE product_category_dim (
    category_key INT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    vertical VARCHAR(50) NOT NULL
) COMMENT = 'Energy product categories: Electricity, Gas, Solar, Heat Pumps, Smart Home, E-Mobility';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Product Dimension (Energy products/tariffs)
CREATE OR REPLACE TABLE product_dim (
    product_key INT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_key INT NOT NULL,
    category_name VARCHAR(100),
    vertical VARCHAR(50)
) COMMENT = 'Energy products: EPOWER Strom, Gas, Solar, Wärmepumpe offerings';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Customer Dimension (German residential and business customers)
CREATE OR REPLACE TABLE customer_dim (
    customer_key INT PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    customer_type VARCHAR(50),
    housing_type VARCHAR(100),
    vertical VARCHAR(50),
    address VARCHAR(200),
    city VARCHAR(100),
    zip VARCHAR(20),
    state VARCHAR(50),
    cluster_id VARCHAR(20),
    region_key INT
) COMMENT = 'German energy customers with housing type and VPP cluster assignment';

-- VPP Cluster Dimension (geographic cluster definitions with centroids)
CREATE OR REPLACE TABLE vpp_cluster_dim (
    cluster_id VARCHAR(20) PRIMARY KEY,
    cluster_name VARCHAR(100),
    centroid_lat FLOAT,
    centroid_lng FLOAT,
    region_character VARCHAR(200),
    compass_region VARCHAR(10)
) COMMENT = 'VPP geographic clusters with centroid coordinates for map visualization';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Vendor Dimension (Installation and service partners)
CREATE OR REPLACE TABLE vendor_dim (
    vendor_key INT PRIMARY KEY,
    vendor_name VARCHAR(200) NOT NULL,
    vendor_type VARCHAR(100),
    vertical VARCHAR(50),
    address VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20)
) COMMENT = 'Installation partners, service providers, and suppliers';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Additional Dimension Tables
CREATE OR REPLACE TABLE account_dim (
    account_key INT PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    account_type VARCHAR(50)
);

CREATE OR REPLACE TABLE department_dim (
    department_key INT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL
) COMMENT = 'EPOWER organizational departments';

CREATE OR REPLACE TABLE region_dim (
    region_key INT PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL
) COMMENT = 'German geographic regions: North, South, West, East';

CREATE OR REPLACE TABLE sales_rep_dim (
    sales_rep_key INT PRIMARY KEY,
    rep_name VARCHAR(200) NOT NULL,
    hire_date DATE
) COMMENT = 'Energy consultants and sales representatives';

CREATE OR REPLACE TABLE campaign_dim (
    campaign_key INT PRIMARY KEY,
    campaign_name VARCHAR(300) NOT NULL,
    objective VARCHAR(100)
) COMMENT = 'Marketing campaigns for energy products';

CREATE OR REPLACE TABLE channel_dim (
    channel_key INT PRIMARY KEY,
    channel_name VARCHAR(100) NOT NULL
);

CREATE OR REPLACE TABLE employee_dim (
    employee_key INT PRIMARY KEY,
    employee_name VARCHAR(200) NOT NULL,
    gender VARCHAR(1),
    hire_date DATE
);

CREATE OR REPLACE TABLE job_dim (
    job_key INT PRIMARY KEY,
    job_title VARCHAR(100) NOT NULL,
    job_level INT
);

CREATE OR REPLACE TABLE location_dim (
    location_key INT PRIMARY KEY,
    location_name VARCHAR(200) NOT NULL
);"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 6. Data Model - Fact Tables <a id="6-fact-tables"></a>

### Concept: Fact Tables

Fact tables contain:
- **Metrics/Measures**: Numeric values (amount, quantity, consumption)
- **Foreign Keys**: Links to dimension tables
- **Timestamps**: When the event occurred

Our EPOWER demo has **6 fact tables** covering:

| Fact Table | Business Domain |
|------------|----------------|
| `sales_fact` | Energy contracts and sales |
| `billing_history` | Consumption and invoicing |
| `service_logs` | Customer service tickets |
| `finance_transactions` | Financial operations |
| `marketing_campaign_fact` | Campaign performance |
| `hr_employee_fact` | Human resources |"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Sales Fact Table (Energy contracts)
CREATE OR REPLACE TABLE sales_fact (
    sale_id INT PRIMARY KEY,
    date DATE NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    sales_rep_key INT NOT NULL,
    region_key INT NOT NULL,
    vendor_key INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    units INT NOT NULL
) COMMENT = 'Energy contracts and product sales. Amount in EUR, Units = kWh for tariffs or count for hardware';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Billing History Table (Energy-specific)
CREATE OR REPLACE TABLE billing_history (
    billing_id INT PRIMARY KEY,
    customer_key INT NOT NULL,
    billing_date DATE NOT NULL,
    billing_type VARCHAR(50) NOT NULL,
    consumption_kwh INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(50)
) COMMENT = 'Monthly energy consumption and billing. billing_type = Electricity or Gas';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Service Logs Table (Customer service tickets)
CREATE OR REPLACE TABLE service_logs (
    log_id INT PRIMARY KEY,
    customer_key INT NOT NULL,
    log_date DATE NOT NULL,
    topic VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    description VARCHAR(500),
    sentiment VARCHAR(50),
    channel VARCHAR(50),
    priority VARCHAR(50),
    resolution_date DATE,
    agent_key INT
) COMMENT = 'Customer service tickets. Sentiment = Positiv/Neutral/Negativ';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Finance, Marketing, and HR Fact Tables
CREATE OR REPLACE TABLE finance_transactions (
    transaction_id INT PRIMARY KEY,
    date DATE NOT NULL,
    account_key INT NOT NULL,
    department_key INT NOT NULL,
    vendor_key INT NOT NULL,
    product_key INT NOT NULL,
    customer_key INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    approval_status VARCHAR(20) DEFAULT 'Pending',
    procurement_method VARCHAR(50),
    approver_id INT,
    approval_date DATE,
    purchase_order_number VARCHAR(50),
    contract_reference VARCHAR(100)
);

CREATE OR REPLACE TABLE marketing_campaign_fact (
    campaign_fact_id INT PRIMARY KEY,
    date DATE NOT NULL,
    campaign_key INT NOT NULL,
    product_key INT NOT NULL,
    channel_key INT NOT NULL,
    region_key INT NOT NULL,
    spend DECIMAL(10,2) NOT NULL,
    leads_generated INT NOT NULL,
    impressions INT NOT NULL
);

CREATE OR REPLACE TABLE hr_employee_fact (
    hr_fact_id INT PRIMARY KEY,
    date DATE NOT NULL,
    employee_key INT NOT NULL,
    department_key INT NOT NULL,
    job_key INT NOT NULL,
    location_key INT NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    attrition_flag INT NOT NULL
);"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Salesforce CRM Tables
CREATE OR REPLACE TABLE sf_accounts (
    account_id VARCHAR(20) PRIMARY KEY,
    account_name VARCHAR(200) NOT NULL,
    customer_key INT NOT NULL,
    industry VARCHAR(100),
    vertical VARCHAR(50),
    billing_street VARCHAR(200),
    billing_city VARCHAR(100),
    billing_state VARCHAR(50),
    billing_postal_code VARCHAR(20),
    account_type VARCHAR(50),
    annual_revenue DECIMAL(15,2),
    employees INT,
    created_date DATE
);

CREATE OR REPLACE TABLE sf_opportunities (
    opportunity_id VARCHAR(20) PRIMARY KEY,
    sale_id INT,
    account_id VARCHAR(20) NOT NULL,
    opportunity_name VARCHAR(200) NOT NULL,
    stage_name VARCHAR(100) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    probability DECIMAL(5,2),
    close_date DATE,
    created_date DATE,
    lead_source VARCHAR(100),
    type VARCHAR(100),
    campaign_id INT
);

CREATE OR REPLACE TABLE sf_contacts (
    contact_id VARCHAR(20) PRIMARY KEY,
    opportunity_id VARCHAR(20) NOT NULL,
    account_id VARCHAR(20) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(200),
    phone VARCHAR(50),
    title VARCHAR(100),
    department VARCHAR(100),
    lead_source VARCHAR(100),
    campaign_no INT,
    created_date DATE
);"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 7. Data Loading from Git Repository <a id="7-data-loading"></a>

### Concept: Direct Loading from Git

One of the powerful features of Snowflake's Git integration is the ability to **COPY INTO tables directly from Git repository stages** - no intermediate staging required!

**Stage Path Format:**
```
@<REPOSITORY_NAME>/branches/<BRANCH_NAME>/<PATH>/<FILE>.csv
```

This approach:
- Eliminates data duplication
- Keeps data version-controlled
- Simplifies the data pipeline"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Load Dimension Tables directly from Git repository
COPY INTO product_category_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/product_category_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO product_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/product_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO customer_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/customer_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO vendor_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/vendor_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO account_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/account_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO department_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/department_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO region_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/region_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO sales_rep_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/sales_rep_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO campaign_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/campaign_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO channel_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/channel_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO employee_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/employee_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO job_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/job_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO location_dim FROM @EPOWER_DEMO_REPO/branches/main/demo_data/location_dim.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Load Fact Tables
COPY INTO sales_fact FROM @EPOWER_DEMO_REPO/branches/main/demo_data/sales_fact.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO billing_history FROM @EPOWER_DEMO_REPO/branches/main/demo_data/billing_history.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO service_logs FROM @EPOWER_DEMO_REPO/branches/main/demo_data/service_logs.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO finance_transactions FROM @EPOWER_DEMO_REPO/branches/main/demo_data/finance_transactions.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO marketing_campaign_fact FROM @EPOWER_DEMO_REPO/branches/main/demo_data/marketing_campaign_fact.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO hr_employee_fact FROM @EPOWER_DEMO_REPO/branches/main/demo_data/hr_employee_fact.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Load Salesforce CRM Tables
COPY INTO sf_accounts FROM @EPOWER_DEMO_REPO/branches/main/demo_data/sf_accounts.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO sf_opportunities FROM @EPOWER_DEMO_REPO/branches/main/demo_data/sf_opportunities.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';
COPY INTO sf_contacts FROM @EPOWER_DEMO_REPO/branches/main/demo_data/sf_contacts.csv FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Verify data loading
SELECT 'DIMENSION TABLES' as category, '' as table_name, NULL as row_count
UNION ALL SELECT '', 'product_category_dim', COUNT(*) FROM product_category_dim
UNION ALL SELECT '', 'product_dim', COUNT(*) FROM product_dim
UNION ALL SELECT '', 'customer_dim', COUNT(*) FROM customer_dim
UNION ALL SELECT '', 'vendor_dim', COUNT(*) FROM vendor_dim
UNION ALL SELECT '', 'region_dim', COUNT(*) FROM region_dim
UNION ALL SELECT '', '', NULL
UNION ALL SELECT 'FACT TABLES', '', NULL
UNION ALL SELECT '', 'sales_fact', COUNT(*) FROM sales_fact
UNION ALL SELECT '', 'billing_history', COUNT(*) FROM billing_history
UNION ALL SELECT '', 'service_logs', COUNT(*) FROM service_logs
UNION ALL SELECT '', 'finance_transactions', COUNT(*) FROM finance_transactions
UNION ALL SELECT '', 'marketing_campaign_fact', COUNT(*) FROM marketing_campaign_fact
UNION ALL SELECT '', 'hr_employee_fact', COUNT(*) FROM hr_employee_fact;"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 8. Semantic Views for Cortex Analyst <a id="8-semantic-views"></a>

### Concept: Semantic Views

**Semantic Views** are a powerful Snowflake feature that bridges the gap between technical data models and business understanding. They enable:

1. **Natural Language Queries**: Ask questions in plain German or English
2. **Business Vocabulary**: Define synonyms (e.g., "Kunden" = "customers")
3. **Pre-defined Metrics**: Common calculations ready to use
4. **Relationship Mapping**: Automatic joins between tables

**How Cortex Analyst Uses Semantic Views:**

```
User Question: "What were total sales by region last quarter?"
       |
       v
+--------------------+
|   CORTEX ANALYST   |
| (LLM + Semantic    |
|     Context)       |
+--------------------+
          |
          v
   Generated SQL Query
```

We'll create **4 Semantic Views** for different business domains."""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- ENERGY SALES SEMANTIC VIEW (Contracts and Products)
CREATE OR REPLACE SEMANTIC VIEW EPOWER_DEMO.EPOWER_GOLD.ENERGY_SALES_SEMANTIC_VIEW
    tables (
        CUSTOMERS as EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_DIM primary key (CUSTOMER_KEY) 
            with synonyms=('Kunden','customers','Privatkunden','Gewerbekunden') 
            comment='German energy customers with housing type for consumption analysis',
        PRODUCTS as EPOWER_DEMO.EPOWER_GOLD.PRODUCT_DIM primary key (PRODUCT_KEY) 
            with synonyms=('Produkte','Tarife','products','tariffs') 
            comment='Energy products: Strom, Gas, Solar, Waermepumpe, Smart Home, E-Mobility',
        PRODUCT_CATEGORIES as EPOWER_DEMO.EPOWER_GOLD.PRODUCT_CATEGORY_DIM primary key (CATEGORY_KEY)
            with synonyms=('Kategorien','categories')
            comment='Product categories: Electricity, Gas, Solar, Heat Pumps, Smart Home, E-Mobility',
        REGIONS as EPOWER_DEMO.EPOWER_GOLD.REGION_DIM primary key (REGION_KEY) 
            with synonyms=('Regionen','regions','Gebiete') 
            comment='German regions: North, South, West, East',
        CONTRACTS as EPOWER_DEMO.EPOWER_GOLD.SALES_FACT primary key (SALE_ID) 
            with synonyms=('Vertraege','contracts','sales','Auftraege') 
            comment='Energy contracts and product sales',
        SALES_REPS as EPOWER_DEMO.EPOWER_GOLD.SALES_REP_DIM primary key (SALES_REP_KEY) 
            with synonyms=('Berater','Energieberater','consultants') 
            comment='Energy consultants',
        VENDORS as EPOWER_DEMO.EPOWER_GOLD.VENDOR_DIM primary key (VENDOR_KEY) 
            with synonyms=('Partner','Installateure','vendors','suppliers') 
            comment='Installation and service partners'
    )
    relationships (
        PRODUCT_TO_CATEGORY as PRODUCTS(CATEGORY_KEY) references PRODUCT_CATEGORIES(CATEGORY_KEY),
        CONTRACTS_TO_CUSTOMERS as CONTRACTS(CUSTOMER_KEY) references CUSTOMERS(CUSTOMER_KEY),
        CONTRACTS_TO_PRODUCTS as CONTRACTS(PRODUCT_KEY) references PRODUCTS(PRODUCT_KEY),
        CONTRACTS_TO_REGIONS as CONTRACTS(REGION_KEY) references REGIONS(REGION_KEY),
        CONTRACTS_TO_REPS as CONTRACTS(SALES_REP_KEY) references SALES_REPS(SALES_REP_KEY),
        CONTRACTS_TO_VENDORS as CONTRACTS(VENDOR_KEY) references VENDORS(VENDOR_KEY),
        CUSTOMERS_TO_REGIONS as CUSTOMERS(REGION_KEY) references REGIONS(REGION_KEY)
    )
    facts (
        CONTRACTS.CONTRACT_AMOUNT as AMOUNT comment='Contract value in EUR',
        CONTRACTS.CONTRACT_UNITS as UNITS comment='kWh for tariffs or unit count for hardware',
        CONTRACTS.CONTRACT_RECORD as 1 comment='Count of contracts'
    )
    dimensions (
        CUSTOMERS.CUSTOMER_KEY as CUSTOMER_KEY,
        CUSTOMERS.CUSTOMER_NAME as customer_name with synonyms=('Kunde','Name') comment='Customer name',
        CUSTOMERS.CUSTOMER_TYPE as customer_type with synonyms=('Kundentyp','Segment') comment='Privatkunde, Kleingewerbe, Gewerbekunde',
        CUSTOMERS.HOUSING_TYPE as housing_type with synonyms=('Wohnform','Gebaeudetyp') comment='Einfamilienhaus, Reihenhaus, Wohnung, etc.',
        CUSTOMERS.CITY as city with synonyms=('Stadt','Ort') comment='German city',
        CUSTOMERS.STATE as state with synonyms=('Region','Bundesland') comment='North, South, West, East',
        PRODUCTS.PRODUCT_KEY as PRODUCT_KEY,
        PRODUCTS.PRODUCT_NAME as product_name with synonyms=('Produkt','Tarif') comment='Product/tariff name',
        PRODUCTS.CATEGORY_NAME as category_name with synonyms=('Kategorie') comment='Product category',
        PRODUCTS.VERTICAL as vertical with synonyms=('Bereich','Segment') comment='Energy, Future Energy, Smart Home, E-Mobility',
        PRODUCT_CATEGORIES.CATEGORY_KEY as CATEGORY_KEY,
        PRODUCT_CATEGORIES.CATEGORY_NAME as MAIN_CATEGORY with synonyms=('Produktkategorie','product_category','main_category') comment='Electricity, Gas, Solar, Heat Pumps, Smart Home, E-Mobility',
        REGIONS.REGION_KEY as REGION_KEY,
        REGIONS.REGION_NAME as region_name with synonyms=('Region','Gebiet') comment='German region',
        CONTRACTS.SALE_ID as SALE_ID,
        CONTRACTS.DATE as CONTRACT_DATE with synonyms=('Vertragsdatum','Datum') comment='Contract date',
        CONTRACTS.SALES_REP_KEY as SALES_REP_KEY,
        SALES_REPS.REP_NAME as rep_name with synonyms=('Berater','Vertriebsmitarbeiter') comment='Energy consultant name',
        VENDORS.VENDOR_KEY as VENDOR_KEY,
        VENDORS.VENDOR_NAME as vendor_name with synonyms=('Partner','Installateur') comment='Installation partner'
    )
    metrics (
        CONTRACTS.TOTAL_REVENUE as SUM(contracts.contract_amount) comment='Total contract revenue in EUR',
        CONTRACTS.TOTAL_CONTRACTS as COUNT(contracts.contract_record) comment='Total number of contracts',
        CONTRACTS.AVERAGE_CONTRACT_VALUE as AVG(contracts.contract_amount) comment='Average contract value',
        CONTRACTS.TOTAL_UNITS as SUM(contracts.contract_units) comment='Total units sold'
    )
    comment='Semantic view for energy sales analysis - contracts, products, customers';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- BILLING AND CONSUMPTION SEMANTIC VIEW
CREATE OR REPLACE SEMANTIC VIEW EPOWER_DEMO.EPOWER_GOLD.BILLING_SEMANTIC_VIEW
    tables (
        CUSTOMERS as EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_DIM primary key (CUSTOMER_KEY)
            with synonyms=('Kunden','customers')
            comment='Energy customers',
        BILLING as EPOWER_DEMO.EPOWER_GOLD.BILLING_HISTORY primary key (BILLING_ID)
            with synonyms=('Rechnungen','Abrechnungen','billing','invoices')
            comment='Monthly energy billing and consumption'
    )
    relationships (
        BILLING_TO_CUSTOMERS as BILLING(CUSTOMER_KEY) references CUSTOMERS(CUSTOMER_KEY)
    )
    facts (
        BILLING.CONSUMPTION as CONSUMPTION_KWH comment='Energy consumption in kWh',
        BILLING.BILLING_AMOUNT as AMOUNT comment='Invoice amount in EUR',
        BILLING.BILLING_RECORD as 1 comment='Count of billing records'
    )
    dimensions (
        CUSTOMERS.CUSTOMER_KEY as CUSTOMER_KEY,
        CUSTOMERS.CUSTOMER_NAME as customer_name comment='Customer name',
        CUSTOMERS.HOUSING_TYPE as housing_type comment='Housing type',
        CUSTOMERS.CITY as city comment='City',
        BILLING.BILLING_ID as BILLING_ID,
        BILLING.BILLING_DATE as billing_date with synonyms=('Rechnungsdatum','Abrechnungsdatum') comment='Billing date',
        BILLING.BILLING_TYPE as billing_type with synonyms=('Energieart','Art') comment='Electricity or Gas',
        BILLING.PAYMENT_STATUS as payment_status with synonyms=('Zahlungsstatus','Status') comment='Bezahlt, Offen, Ueberfaellig'
    )
    metrics (
        BILLING.TOTAL_CONSUMPTION as SUM(billing.consumption) comment='Total consumption in kWh',
        BILLING.AVERAGE_CONSUMPTION as AVG(billing.consumption) comment='Average consumption in kWh',
        BILLING.TOTAL_BILLING_AMOUNT as SUM(billing.billing_amount) comment='Total billing amount',
        BILLING.TOTAL_INVOICES as COUNT(billing.billing_record) comment='Number of invoices'
    )
    comment='Semantic view for energy consumption and billing analysis';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- SERVICE LOGS SEMANTIC VIEW
CREATE OR REPLACE SEMANTIC VIEW EPOWER_DEMO.EPOWER_GOLD.SERVICE_SEMANTIC_VIEW
    tables (
        CUSTOMERS as EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_DIM primary key (CUSTOMER_KEY)
            with synonyms=('Kunden','customers')
            comment='Energy customers',
        SERVICE_TICKETS as EPOWER_DEMO.EPOWER_GOLD.SERVICE_LOGS primary key (LOG_ID)
            with synonyms=('Tickets','Anfragen','service requests','Kundenservice')
            comment='Customer service tickets and support requests'
    )
    relationships (
        SERVICE_TO_CUSTOMERS as SERVICE_TICKETS(CUSTOMER_KEY) references CUSTOMERS(CUSTOMER_KEY)
    )
    facts (
        SERVICE_TICKETS.TICKET_RECORD as 1 comment='Count of service tickets'
    )
    dimensions (
        CUSTOMERS.CUSTOMER_KEY as CUSTOMER_KEY,
        CUSTOMERS.CUSTOMER_NAME as customer_name comment='Customer name',
        CUSTOMERS.CITY as city comment='City',
        SERVICE_TICKETS.LOG_ID as TICKET_ID,
        SERVICE_TICKETS.LOG_DATE as ticket_date with synonyms=('Datum','Erstelldatum') comment='Ticket creation date',
        SERVICE_TICKETS.TOPIC as topic with synonyms=('Thema','Betreff') comment='Topic: Smart Meter, Rechnung, Waermepumpe, Solar, Tarif, Wallbox, Allgemein',
        SERVICE_TICKETS.CATEGORY as category with synonyms=('Kategorie') comment='Category: Installation, Abrechnung, Technisch, Vertrag, E-Mobility, Service',
        SERVICE_TICKETS.DESCRIPTION as description with synonyms=('Beschreibung','Details') comment='Ticket description',
        SERVICE_TICKETS.SENTIMENT as sentiment with synonyms=('Stimmung','Bewertung') comment='Customer sentiment: Positiv, Neutral, Negativ',
        SERVICE_TICKETS.CHANNEL as channel with synonyms=('Kanal','Kontaktweg') comment='Contact channel: Telefon, Email, Chat, App',
        SERVICE_TICKETS.PRIORITY as priority with synonyms=('Prioritaet','Dringlichkeit') comment='Priority: Niedrig, Mittel, Hoch, Kritisch',
        SERVICE_TICKETS.RESOLUTION_DATE as resolution_date with synonyms=('Loesungsdatum') comment='Resolution date'
    )
    metrics (
        SERVICE_TICKETS.TOTAL_TICKETS as COUNT(service_tickets.ticket_record) comment='Total number of tickets',
        SERVICE_TICKETS.NEGATIVE_TICKETS as SUM(CASE WHEN service_tickets.sentiment = 'Negativ' THEN 1 ELSE 0 END) comment='Negative sentiment tickets'
    )
    comment='Semantic view for customer service analysis';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- HR SEMANTIC VIEW
CREATE OR REPLACE SEMANTIC VIEW EPOWER_DEMO.EPOWER_GOLD.HR_SEMANTIC_VIEW
    tables (
        DEPARTMENTS as EPOWER_DEMO.EPOWER_GOLD.DEPARTMENT_DIM primary key (DEPARTMENT_KEY)
            with synonyms=('Abteilungen','departments')
            comment='Company departments',
        EMPLOYEES as EPOWER_DEMO.EPOWER_GOLD.EMPLOYEE_DIM primary key (EMPLOYEE_KEY)
            with synonyms=('Mitarbeiter','employees','Personal')
            comment='Employees',
        HR_RECORDS as EPOWER_DEMO.EPOWER_GOLD.HR_EMPLOYEE_FACT primary key (HR_FACT_ID)
            with synonyms=('HR-Daten','hr records')
            comment='HR fact records',
        JOBS as EPOWER_DEMO.EPOWER_GOLD.JOB_DIM primary key (JOB_KEY)
            with synonyms=('Stellen','jobs','Positionen')
            comment='Job positions',
        LOCATIONS as EPOWER_DEMO.EPOWER_GOLD.LOCATION_DIM primary key (LOCATION_KEY)
            with synonyms=('Standorte','locations')
            comment='Office locations'
    )
    relationships (
        HR_TO_DEPARTMENTS as HR_RECORDS(DEPARTMENT_KEY) references DEPARTMENTS(DEPARTMENT_KEY),
        HR_TO_EMPLOYEES as HR_RECORDS(EMPLOYEE_KEY) references EMPLOYEES(EMPLOYEE_KEY),
        HR_TO_JOBS as HR_RECORDS(JOB_KEY) references JOBS(JOB_KEY),
        HR_TO_LOCATIONS as HR_RECORDS(LOCATION_KEY) references LOCATIONS(LOCATION_KEY)
    )
    facts (
        HR_RECORDS.ATTRITION_FLAG as ATTRITION_FLAG comment='1 = employee left, 0 = active',
        HR_RECORDS.EMPLOYEE_SALARY as SALARY comment='Salary in EUR',
        HR_RECORDS.HR_RECORD as 1 comment='HR record count',
        EMPLOYEES.EMPLOYEE_COUNT as 1 comment='Employee count'
    )
    dimensions (
        DEPARTMENTS.DEPARTMENT_KEY as DEPARTMENT_KEY,
        DEPARTMENTS.DEPARTMENT_NAME as department_name with synonyms=('Abteilung') comment='Department name',
        EMPLOYEES.EMPLOYEE_KEY as EMPLOYEE_KEY,
        EMPLOYEES.EMPLOYEE_NAME as employee_name with synonyms=('Mitarbeiter','Name') comment='Employee name',
        EMPLOYEES.GENDER as gender with synonyms=('Geschlecht') comment='M or F',
        EMPLOYEES.HIRE_DATE as hire_date with synonyms=('Eintrittsdatum') comment='Hire date',
        HR_RECORDS.DATE as record_date comment='HR record date',
        JOBS.JOB_KEY as JOB_KEY,
        JOBS.JOB_TITLE as job_title with synonyms=('Position','Stelle') comment='Job title',
        JOBS.JOB_LEVEL as job_level with synonyms=('Ebene','Level') comment='Job level',
        LOCATIONS.LOCATION_KEY as LOCATION_KEY,
        LOCATIONS.LOCATION_NAME as location_name with synonyms=('Standort') comment='Office location'
    )
    metrics (
        HR_RECORDS.TOTAL_SALARY as SUM(hr_records.employee_salary) comment='Total salary cost',
        HR_RECORDS.AVG_SALARY as AVG(hr_records.employee_salary) comment='Average salary',
        HR_RECORDS.ATTRITION_COUNT as SUM(hr_records.attrition_flag) comment='Attrition count',
        EMPLOYEES.TOTAL_EMPLOYEES as COUNT(employees.employee_count) comment='Total employees'
    )
    comment='Semantic view for HR analytics';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": "-- Verify semantic views\\nSHOW SEMANTIC VIEWS;"
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 9. Unstructured Data Processing <a id="9-unstructured-data"></a>

### Concept: Cortex Parse Document

**Cortex Parse** is a Snowflake feature that extracts text and structure from unstructured documents:

- **PDF documents**: Contracts, guides, policies
- **Markdown files**: Documentation, FAQs
- **Layout preservation**: Maintains document structure

**Modes:**
- `OCR`: Optical character recognition for scanned documents
- `LAYOUT`: Preserves document layout and structure (recommended)

This parsed content becomes searchable via **Cortex Search**."""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Parse PDF and Markdown documents
CREATE OR REPLACE TABLE parsed_content AS 
SELECT 
    relative_path,
    BUILD_STAGE_FILE_URL('@EPOWER_DEMO.EPOWER_GOLD.EPOWER_STAGE', relative_path) as file_url,
    TO_FILE(BUILD_STAGE_FILE_URL('@EPOWER_DEMO.EPOWER_GOLD.EPOWER_STAGE', relative_path)) file_object,
    SNOWFLAKE.CORTEX.PARSE_DOCUMENT(
        @EPOWER_DEMO.EPOWER_GOLD.EPOWER_STAGE,
        relative_path,
        {'mode':'LAYOUT'}
    ):content::string as content
FROM directory(@EPOWER_DEMO.EPOWER_GOLD.EPOWER_STAGE) 
WHERE relative_path ILIKE 'unstructured_docs/%.pdf' 
   OR relative_path ILIKE 'unstructured_docs/%.md';"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Verify parsed documents
SELECT relative_path, LEFT(content, 200) as content_preview 
FROM parsed_content 
LIMIT 5;"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 10. Cortex Search Services <a id="10-cortex-search"></a>

### Concept: Cortex Search

**Cortex Search** provides vector-based semantic search over your data:

- Uses embedding models to convert text to vectors
- Finds semantically similar content (not just keyword matching)
- Ideal for RAG (Retrieval Augmented Generation) applications

**Key Parameters:**
- `ON`: The column to search (the content)
- `ATTRIBUTES`: Metadata columns to return
- `TARGET_LAG`: How often to refresh the index
- `EMBEDDING_MODEL`: The model for vectorization

We create **4 search services** for different document types."""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Search service for energy policy documents
CREATE OR REPLACE CORTEX SEARCH SERVICE Search_energy_docs
    ON content
    ATTRIBUTES relative_path, file_url, title
    WAREHOUSE = EPOWER_COMPUTE
    TARGET_LAG = '30 day'
    EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
    AS (
        SELECT
            relative_path,
            file_url,
            REGEXP_SUBSTR(relative_path, '[^/]+$') as title,
            content
        FROM parsed_content
        WHERE relative_path ILIKE '%/energy/%'
    );"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Search service for product documents
CREATE OR REPLACE CORTEX SEARCH SERVICE Search_product_docs
    ON content
    ATTRIBUTES relative_path, file_url, title
    WAREHOUSE = EPOWER_COMPUTE
    TARGET_LAG = '30 day'
    EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
    AS (
        SELECT
            relative_path,
            file_url,
            REGEXP_SUBSTR(relative_path, '[^/]+$') as title,
            content
        FROM parsed_content
        WHERE relative_path ILIKE '%/products/%'
    );"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Search service for customer service documents
CREATE OR REPLACE CORTEX SEARCH SERVICE Search_service_docs
    ON content
    ATTRIBUTES relative_path, file_url, title
    WAREHOUSE = EPOWER_COMPUTE
    TARGET_LAG = '30 day'
    EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
    AS (
        SELECT
            relative_path,
            file_url,
            REGEXP_SUBSTR(relative_path, '[^/]+$') as title,
            content
        FROM parsed_content
        WHERE relative_path ILIKE '%/service/%'
    );"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Search service for service logs (structured data search)
CREATE OR REPLACE CORTEX SEARCH SERVICE Search_service_logs
    ON description
    ATTRIBUTES log_id, customer_key, topic, category, sentiment, priority
    WAREHOUSE = EPOWER_COMPUTE
    TARGET_LAG = '1 day'
    EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
    AS (
        SELECT
            log_id,
            customer_key,
            topic,
            category,
            description,
            sentiment,
            priority
        FROM service_logs
    );"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": "-- Verify search services\\nSHOW CORTEX SEARCH SERVICES;"
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 11. Snowflake Intelligence Agent <a id="11-agent"></a>

### Concept: Snowflake Intelligence Agent

A **Snowflake Intelligence Agent** is an AI orchestrator that can:

1. **Understand natural language** - Process questions in German or English
2. **Select appropriate tools** - Choose between Text-to-SQL, Search, Web Scraping
3. **Execute multi-step tasks** - Chain tool calls together
4. **Return formatted responses** - With data, visualizations, and citations

### Setting up External Access (for Web Scraping)"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Create network rule for web access
CREATE OR REPLACE NETWORK RULE Energy_Intelligence_WebAccessRule
    MODE = EGRESS
    TYPE = HOST_PORT
    VALUE_LIST = ('0.0.0.0:80', '0.0.0.0:443');"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Create external access integration (requires ACCOUNTADMIN)
USE ROLE accountadmin;

GRANT ALL PRIVILEGES ON DATABASE EPOWER_DEMO TO ROLE ACCOUNTADMIN;
GRANT ALL PRIVILEGES ON SCHEMA EPOWER_DEMO.EPOWER_GOLD TO ROLE ACCOUNTADMIN;
GRANT USAGE ON NETWORK RULE EPOWER_DEMO.EPOWER_GOLD.Energy_Intelligence_WebAccessRule TO ROLE accountadmin;

USE SCHEMA EPOWER_DEMO.EPOWER_GOLD;

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION Energy_Intelligence_ExternalAccess_Integration
    ALLOWED_NETWORK_RULES = (Energy_Intelligence_WebAccessRule)
    ENABLED = true;

GRANT USAGE ON INTEGRATION Energy_Intelligence_ExternalAccess_Integration TO ROLE EPOWER_ROLE;"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Create helper functions
USE ROLE EPOWER_ROLE;

-- Presigned URL procedure for file access
CREATE OR REPLACE PROCEDURE Get_File_Presigned_URL_SP(
    RELATIVE_FILE_PATH STRING, 
    EXPIRATION_MINS INTEGER DEFAULT 60
)
RETURNS STRING
LANGUAGE SQL
COMMENT = 'Generates a presigned URL for files in EPOWER_STAGE'
EXECUTE AS CALLER
AS
$$
DECLARE
    presigned_url STRING;
    sql_stmt STRING;
    expiration_seconds INTEGER;
    stage_name STRING DEFAULT '@EPOWER_DEMO.EPOWER_GOLD.EPOWER_STAGE';
BEGIN
    expiration_seconds := EXPIRATION_MINS * 60;
    sql_stmt := 'SELECT GET_PRESIGNED_URL(' || stage_name || ', ' || '''' || RELATIVE_FILE_PATH || '''' || ', ' || expiration_seconds || ') AS url';
    EXECUTE IMMEDIATE :sql_stmt;
    SELECT "URL" INTO :presigned_url FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));
    RETURN :presigned_url;
END;
$$;"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Web scraping function
CREATE OR REPLACE FUNCTION Web_scrape(weburl STRING)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = 3.11
HANDLER = 'get_page'
EXTERNAL_ACCESS_INTEGRATIONS = (Energy_Intelligence_ExternalAccess_Integration)
PACKAGES = ('requests', 'beautifulsoup4')
AS
$$
import requests
from bs4 import BeautifulSoup

def get_page(weburl):
    response = requests.get(weburl)
    soup = BeautifulSoup(response.text)
    return soup.get_text()
$$;"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """### Creating the Intelligence Agent

The agent specification defines:
- **Instructions**: How the agent should behave and respond
- **Tools**: Available capabilities (Cortex Analyst, Cortex Search, Functions)
- **Tool Resources**: Configuration for each tool"""
})

agent_spec = '''{
  "models": {
    "orchestration": ""
  },
  "instructions": {
    "response": "Du bist ein Datenanalyst fuer EPOWER Energie Deutschland. Du hast Zugriff auf Energie-Vertriebsdaten (Strom, Gas, Solar, Waermepumpen, Smart Home, E-Mobility), Verbrauchsabrechnungen, Kundenservice-Tickets und interne Dokumente. Antworte auf Deutsch, wenn der Nutzer auf Deutsch fragt. Liefere Visualisierungen wenn moeglich.",
    "orchestration": "Nutze Cortex Search fuer Dokumente und Cortex Analyst fuer strukturierte Datenanalysen. Bei Fragen zu Verbrauch, nutze das Billing Datamart. Bei Fragen zu Service-Tickets oder Beschwerden, nutze das Service Datamart. Bei Produktfragen, nutze das Energy Sales Datamart.",
    "sample_questions": [
      {"question": "Was ist der durchschnittliche Stromverbrauch fuer Kunden mit Waermepumpen in Hamburg?"},
      {"question": "Zeige mir alle negativen Service-Tickets zum Thema Smart Meter."},
      {"question": "Welche Produkte wurden letzten Monat am meisten verkauft?"}
    ]
  },
  "tools": [
    {"tool_spec": {"type": "cortex_analyst_text_to_sql", "name": "Query Energy Sales", "description": "Analysiert Energievertraege, Produkte (Strom, Gas, Solar, Waermepumpen), Kunden und Regionen."}},
    {"tool_spec": {"type": "cortex_analyst_text_to_sql", "name": "Query Billing Data", "description": "Analysiert Energieverbrauch (kWh), Abrechnungen und Zahlungsstatus fuer Strom und Gas."}},
    {"tool_spec": {"type": "cortex_analyst_text_to_sql", "name": "Query Service Tickets", "description": "Analysiert Kundenservice-Tickets, Beschwerden, Sentiment und Themen wie Smart Meter, Waermepumpe, Solar."}},
    {"tool_spec": {"type": "cortex_analyst_text_to_sql", "name": "Query HR Data", "description": "Analysiert HR-Daten: Mitarbeiter, Gehaelter, Fluktuation, Abteilungen."}},
    {"tool_spec": {"type": "cortex_search", "name": "Search Energy Documents", "description": "Sucht in Energiedokumenten: AGBs, Foerderungen, Richtlinien."}},
    {"tool_spec": {"type": "cortex_search", "name": "Search Product Documents", "description": "Sucht in Produktdokumenten: Waermepumpen-Guide, Solar-Anleitungen, Smart Meter, E-Mobility."}},
    {"tool_spec": {"type": "cortex_search", "name": "Search Service Documents", "description": "Sucht in Service-Dokumenten: Rechnungserklaerungen, Energiespar-Tipps, Kundenservice-Handbuch."}},
    {"tool_spec": {"type": "cortex_search", "name": "Search Service Logs", "description": "Semantische Suche in Service-Tickets nach Beschreibungen und Themen."}},
    {"tool_spec": {"type": "generic", "name": "Web_scraper", "description": "Analysiert Inhalte von Webseiten (z.B. fuer aktuelle Energiepreise, Foerderprogramme).", "input_schema": {"type": "object", "properties": {"weburl": {"description": "URL der Webseite", "type": "string"}}, "required": ["weburl"]}}},
    {"tool_spec": {"type": "generic", "name": "Dynamic_Doc_URL_Tool", "description": "Generiert Download-URLs fuer Dokumente aus dem Stage.", "input_schema": {"type": "object", "properties": {"expiration_mins": {"description": "Gueltigkeit in Minuten (Standard: 5)", "type": "number"}, "relative_file_path": {"description": "Relativer Pfad zur Datei", "type": "string"}}, "required": ["relative_file_path"]}}}
  ],
  "tool_resources": {
    "Query Energy Sales": {"semantic_view": "EPOWER_DEMO.EPOWER_GOLD.ENERGY_SALES_SEMANTIC_VIEW"},
    "Query Billing Data": {"semantic_view": "EPOWER_DEMO.EPOWER_GOLD.BILLING_SEMANTIC_VIEW"},
    "Query Service Tickets": {"semantic_view": "EPOWER_DEMO.EPOWER_GOLD.SERVICE_SEMANTIC_VIEW"},
    "Query HR Data": {"semantic_view": "EPOWER_DEMO.EPOWER_GOLD.HR_SEMANTIC_VIEW"},
    "Search Energy Documents": {"id_column": "RELATIVE_PATH", "max_results": 5, "name": "EPOWER_DEMO.EPOWER_GOLD.SEARCH_ENERGY_DOCS", "title_column": "TITLE"},
    "Search Product Documents": {"id_column": "RELATIVE_PATH", "max_results": 5, "name": "EPOWER_DEMO.EPOWER_GOLD.SEARCH_PRODUCT_DOCS", "title_column": "TITLE"},
    "Search Service Documents": {"id_column": "RELATIVE_PATH", "max_results": 5, "name": "EPOWER_DEMO.EPOWER_GOLD.SEARCH_SERVICE_DOCS", "title_column": "TITLE"},
    "Search Service Logs": {"id_column": "LOG_ID", "max_results": 10, "name": "EPOWER_DEMO.EPOWER_GOLD.SEARCH_SERVICE_LOGS", "title_column": "TOPIC"},
    "Web_scraper": {"execution_environment": {"type": "warehouse", "warehouse": "EPOWER_COMPUTE"}, "identifier": "EPOWER_DEMO.EPOWER_GOLD.WEB_SCRAPE", "name": "WEB_SCRAPE(VARCHAR)", "type": "function"},
    "Dynamic_Doc_URL_Tool": {"execution_environment": {"type": "warehouse", "warehouse": "EPOWER_COMPUTE"}, "identifier": "EPOWER_DEMO.EPOWER_GOLD.GET_FILE_PRESIGNED_URL_SP", "name": "GET_FILE_PRESIGNED_URL_SP(VARCHAR, DEFAULT NUMBER)", "type": "procedure"}
  }
}'''

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": f"""-- Create the Snowflake Intelligence Agent
CREATE OR REPLACE AGENT EPOWER_DEMO.EPOWER_GOLD.Energy_Chatbot_Agent
WITH PROFILE='{{ "display_name": "EPOWER Energy Intelligence Agent" }}'
COMMENT=$$ Agent for energy retail analysis: contracts, consumption, service tickets, and documents. $$
FROM SPECIFICATION $$
{agent_spec}
$$;"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Assign agent to Snowflake Intelligence and grant access
USE ROLE accountadmin;

ALTER SNOWFLAKE INTELLIGENCE snowflake_intelligence_object_default ADD AGENT EPOWER_DEMO.EPOWER_GOLD.Energy_Chatbot_Agent;
GRANT USAGE ON AGENT EPOWER_DEMO.EPOWER_GOLD.Energy_Chatbot_Agent TO ROLE PUBLIC;
GRANT USAGE ON AGENT EPOWER_DEMO.EPOWER_GOLD.Energy_Chatbot_Agent TO ROLE EPOWER_ROLE;

USE ROLE EPOWER_ROLE;"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """---

## 12. Verification & Next Steps <a id="12-verification"></a>

### Setup Complete!

Let's verify everything was created successfully."""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- Final verification
SELECT 'Energy AI Demo Setup Complete!' as status;
SELECT 'Database: EPOWER_DEMO.EPOWER_GOLD' as info;
SELECT 'Agent: Energy_Chatbot_Agent' as info;
SELECT 'Semantic Views: 4 (Energy Sales, Billing, Service, HR)' as info;
SELECT 'Cortex Search: 4 services (Energy, Product, Service docs + Service logs)' as info;"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """-- View all created objects
SHOW TABLES IN SCHEMA EPOWER_DEMO.EPOWER_GOLD;
SHOW SEMANTIC VIEWS IN SCHEMA EPOWER_DEMO.EPOWER_GOLD;
SHOW CORTEX SEARCH SERVICES IN SCHEMA EPOWER_DEMO.EPOWER_GOLD;
SHOW AGENTS IN SCHEMA EPOWER_DEMO.EPOWER_GOLD;"""
})

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": """### Try the Agent!

Now you can interact with the Energy Intelligence Agent. Here are some sample questions to try:

**Sales & Products (German):**
- "Welche Produkte wurden letzten Monat am meisten verkauft?"
- "Zeige mir den Umsatz nach Region fuer 2024"

**Consumption & Billing:**
- "What is the average electricity consumption for customers with heat pumps?"
- "Wie ist der Zahlungsstatus unserer Rechnungen aufgeteilt?"

**Service Tickets:**
- "Zeige mir alle negativen Service-Tickets zum Thema Smart Meter"
- "What are the most common service ticket topics?"

**Document Search (RAG):**
- "Was sind die Voraussetzungen fuer die Waermepumpen-Foerderung?"
- "Erklaere mir, wie ich meine Stromrechnung lesen kann"

### What You've Learned

| Concept | What You Did |
|---------|-------------|
| **Git Integration** | Connected to GitHub, loaded data directly from Git stage |
| **Star Schema** | Created dimension and fact tables for analytical workloads |
| **Semantic Views** | Defined business vocabulary, relationships, and metrics for AI |
| **Cortex Parse** | Extracted text from PDF documents |
| **Cortex Search** | Created vector search indexes for RAG |
| **Intelligence Agent** | Built a multi-tool AI assistant |

### Clean Up (Optional)

To remove all demo resources:

```sql
USE ROLE accountadmin;
DROP DATABASE IF EXISTS EPOWER_DEMO;
DROP WAREHOUSE IF EXISTS EPOWER_COMPUTE;
DROP ROLE IF EXISTS EPOWER_ROLE;
DROP API INTEGRATION IF EXISTS git_api_integration_energy;
DROP EXTERNAL ACCESS INTEGRATION IF EXISTS Energy_Intelligence_ExternalAccess_Integration;
```"""
})

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open('/Users/jjoerg/sfl/dev/cortexcode/Snowflake_AI_Demo_NAkincilar_Projects/Snowflake_AI_DEMO_jojrg/notebooks/demo_setup.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("Notebook created successfully!")
