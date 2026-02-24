# Banking Risk Multi-Agent System

> **Production-ready multi-agent loan risk assessment engine** — combines rule-based and ML-inspired scoring with policy retrieval (RAG) and a full compliance audit trail.

## Architecture

```
                         ┌─────────────────────────────────────────────┐
  POST /api/v1/assess ──►│            CoordinatorAgent                 │
                         │  (orchestrates pipeline, caches in Redis)   │
                         └────────────┬────────────────────────────────┘
                                      │ spawns
              ┌───────────────────────┼──────────────────────┐
              ▼                       ▼                      ▼
  ┌───────────────────┐  ┌─────────────────────┐  ┌──────────────────────┐
  │ CustomerIntent    │  │  RiskScoringAgent   │  │ PolicyValidation     │
  │ Agent             │  │  • DTI ratio        │  │ Agent (RAG)          │
  │ • Purpose risk    │  │  • Credit score     │  │ • ChromaDB stub      │
  │ • Risk indicators │  │  • Amortization     │  │ • 5 policy clauses   │
  │ • Confidence      │  │  • Risk level       │  │ • Compliance check   │
  └───────────────────┘  └─────────────────────┘  └──────────────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │  ComplianceAuditAgent   │
                         │  • Reasoning trace      │
                         │  • Audit report         │
                         │  • Recommendations      │
                         │  • SQLite persistence   │
                         └─────────────────────────┘
```

**Memory layers:**
- 🔴 **Redis** — short-term session cache (TTL 1 h, in-memory fallback)
- 🗄️  **SQLite** — long-term audit log & assessment history

## Quick Start

```bash
cd banking-risk-multi-agent-system
pip install -r requirements.txt
uvicorn src.api.main:app --reload
```

### Example API call

```bash
curl -X POST http://localhost:8000/api/v1/assess \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-001",
    "annual_income": 80000,
    "monthly_debt": 800,
    "loan_amount": 200000,
    "loan_term_months": 360,
    "interest_rate": 5.5,
    "credit_score": 720,
    "employment_years": 5.0,
    "loan_purpose": "home"
  }'
```

### Example JSON response (abbreviated)

```json
{
  "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "customer_id": "CUST-001",
  "decision": "approved",
  "customer_intent": {
    "intent_summary": "Customer CUST-001 is requesting a $200,000 Home loan over 360 months at 5.5% APR. No significant risk indicators detected.",
    "risk_indicators": [],
    "confidence_score": 0.65
  },
  "risk_scoring": {
    "debt_to_income_ratio": 0.12,
    "monthly_payment": 1135.58,
    "risk_score": 0.2891,
    "risk_level": "low",
    "total_interest": 208808.8,
    "total_cost": 408808.8
  },
  "policy_validation": {
    "is_compliant": true,
    "validation_notes": "All policy checks passed.",
    "grounded_assessment": "Based on retrieved policy clauses [POL-004, POL-001, POL-003], the application is compliant..."
  },
  "compliance_audit": {
    "audit_id": "a1b2c3d4-...",
    "is_approved": true,
    "recommendations": ["Application meets all standard criteria. Proceed with standard processing."]
  },
  "processing_time_ms": 3.41
}
```

## Run Tests

```bash
cd banking-risk-multi-agent-system
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

## Docker

```bash
cd banking-risk-multi-agent-system
docker compose -f docker/docker-compose.yml up --build
```

---

# Credit Risk Prediction using Logistic Regression

This project demonstrates an end-to-end **Logistic Regression** pipeline to predict **credit card default risk** using a real-world banking dataset.  
The focus is on **data cleaning, feature selection, model interpretability, and business relevance**, rather than just model accuracy.

---

## Problem Statement

Financial institutions need to assess the risk of a customer defaulting on a loan or credit card payment.

**Objective:**  
Predict whether a customer will **default on their next payment** using historical financial and demographic data.

**Type of problem:**  
Binary Classification  
- `1` → Default  
- `0` → No Default

---

## Dataset

- **Source:** UCI Machine Learning Repository  
- **Dataset Name:** Default of Credit Card Clients Dataset  
- **Records:** 30,000 customers  
- **Domain:** Banking / Credit Risk Analytics  

> Note: The dataset file is not committed to the repository.  
> Please download it manually from the UCI repository and place it in the `data/` directory.

---

## Features Used

The following features were selected based on **industry relevance and interpretability**:

| Feature Name | Description |
|-------------|------------|
| `LIMIT_BAL` | Credit limit assigned to the customer |
| `AGE` | Customer age |
| `PAY_0` | Repayment status of the most recent month |
| `BILL_AMT1` | Last bill amount |
| `PAY_AMT1` | Last payment amount |

**Target Variable**
- `default` → Whether the customer defaults next month

---

## Data Preprocessing

Real-world datasets are rarely clean. This project includes:
- Fixing incorrect Excel headers
- Renaming columns for clarity
- Converting string values to numeric
- Handling missing values
- Explicit feature and target separation

These steps ensure the dataset is **model-ready and reproducible**.

---

## Model Used

### Logistic Regression

Logistic Regression is chosen because:
- It outputs **probabilities**, not just predictions
- Coefficients are **interpretable**
- Widely used in **regulated domains** like banking and finance

The model estimates the probability of default and applies a decision threshold for classification.

---

## Visualizations

The project includes data visualizations to:
- Understand feature impact on default risk
- Explore relationships between variables
- Communicate insights clearly to non-technical stakeholders

Examples:
- Credit limit vs default
- Age distribution by default status
- Probability curves for selected features

---

## Model Evaluation

The model is evaluated using:
- Accuracy
- Confusion Matrix
- Probability predictions (`predict_proba`)

This aligns with **business-driven evaluation**, where risk probabilities matter more than raw accuracy.

---



## How to Run the Project

1. Clone the repository
git clone https://github.com/your-username/credit-risk-logistic-regression.git

2. Install dependencies
pip install -r requirements.txt

3.Run the training script
python src/train_model.py

Or explore the notebook:
jupyter notebook notebooks/credit_risk_analysis.ipynb


## Project Structure
```text
credit-risk-logistic-regression/
│
├── data/
│ └── README.md # Dataset source and download instructions
│
├── notebooks/
│ └── credit_risk_analysis.ipynb
│
├── src/
│ └── train_model.py
│
├── requirements.txt
└── README.md


---

